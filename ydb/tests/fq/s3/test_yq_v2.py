#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import logging

import pytest

from ydb.tests.tools.datastreams_helpers.test_yds_base import TestYdsBase

import ydb.public.api.protos.ydb_value_pb2 as ydb
import ydb.public.api.protos.draft.fq_pb2 as fq

from ydb.tests.tools.fq_runner.kikimr_utils import yq_v2


class TestS3(TestYdsBase):
    @yq_v2
    @pytest.mark.parametrize("client", [{"folder_id": "my_folder"}], indirect=True)
    def test_yqv2_enabled(self, kikimr, s3, client):
        resource = boto3.resource(
            "s3",
            endpoint_url=s3.s3_url,
            aws_access_key_id="key",
            aws_secret_access_key="secret_key"
        )

        bucket = resource.Bucket("fbucket")
        bucket.create(ACL='public-read')

        s3_client = boto3.client(
            "s3",
            endpoint_url=s3.s3_url,
            aws_access_key_id="key",
            aws_secret_access_key="secret_key"
        )

        fruits = R'''Fruit;Price;Duration
Banana;3;100
Apple;2;22
Pear;15;33'''
        s3_client.put_object(Body=fruits, Bucket='fbucket', Key='fruits.csv', ContentType='text/plain')
        kikimr.control_plane.wait_bootstrap(1)
        connection_response = client.create_storage_connection("fruitbucket", "fbucket")

        fruitType = ydb.Column(name="Fruit", type=ydb.Type(type_id=ydb.Type.PrimitiveTypeId.STRING))
        priceType = ydb.Column(name="Price", type=ydb.Type(type_id=ydb.Type.PrimitiveTypeId.INT32))
        intervalType = ydb.Column(name="Duration", type=ydb.Type(type_id=ydb.Type.PrimitiveTypeId.INTERVAL))
        client.create_object_storage_binding(name="my_binding",
                                             path="fruits.csv",
                                             format="csv_with_names",
                                             connection_id=connection_response.result.connection_id,
                                             columns=[fruitType, priceType, intervalType],
                                             format_setting={
                                                 "data.interval.unit": "SECONDS",
                                                 "csv_delimiter": ";"
                                             })

        sql = R'''
            pragma s3.UseBlocksSource="false";
            SELECT *
            FROM my_binding; -- syntax without bindings. supported only in yqv2
            '''

        query_id = client.create_query("simple", sql, type=fq.QueryContent.QueryType.ANALYTICS).result.query_id
        client.wait_query_status(query_id, fq.QueryMeta.COMPLETED)

        data = client.get_result_data(query_id)
        result_set = data.result.result_set
        logging.debug(str(result_set))
        assert len(result_set.columns) == 3
        assert result_set.columns[0].name == "Duration"
        assert result_set.columns[0].type.type_id == ydb.Type.INTERVAL
        assert result_set.columns[1].name == "Fruit"
        assert result_set.columns[1].type.type_id == ydb.Type.STRING
        assert result_set.columns[2].name == "Price"
        assert result_set.columns[2].type.type_id == ydb.Type.INT32
        assert len(result_set.rows) == 3
        assert result_set.rows[0].items[0].int64_value == 100000000
        assert result_set.rows[0].items[1].bytes_value == b"Banana"
        assert result_set.rows[0].items[2].int32_value == 3
        assert result_set.rows[1].items[0].int64_value == 22000000
        assert result_set.rows[1].items[1].bytes_value == b"Apple"
        assert result_set.rows[1].items[2].int32_value == 2
        assert result_set.rows[2].items[0].int64_value == 33000000
        assert result_set.rows[2].items[1].bytes_value == b"Pear"
        assert result_set.rows[2].items[2].int32_value == 15
