#pragma once

#include "common.h"

#include <ydb/public/sdk/cpp/client/ydb_query/query.h>


namespace NKqpRun {

struct TSchemeMeta {
    TString Ast;
};


struct TExecutionMeta {
    bool Ready = false;
    NYdb::NQuery::EExecStatus ExecutionStatus = NYdb::NQuery::EExecStatus::Unspecified;

    i32 ResultSetsCount = 0;

    TString Ast;
    TString Plan;
};


struct TRequestResult {
    Ydb::StatusIds::StatusCode Status;
    NYql::TIssues Issues;

    TRequestResult();

    TRequestResult(Ydb::StatusIds::StatusCode status, const NYql::TIssues& issues);

    bool IsSuccess() const;

    TString ToString() const;
};


class TYdbSetup {
public:
    explicit TYdbSetup(const TYdbSetupSettings& settings);

    TRequestResult SchemeQueryRequest(const TString& query, TSchemeMeta& meta) const;

    TRequestResult ScriptQueryRequest(const TString& script, NKikimrKqp::EQueryAction action, TString& operation) const;

    TRequestResult GetScriptExecutionOperationRequest(const TString& operation, TExecutionMeta& meta) const;

    TRequestResult FetchScriptExecutionResultsRequest(const TString& operation, i32 resultSetId, i64 limit, Ydb::ResultSet& resultSet) const;

private:
    class TImpl;
    std::shared_ptr<TImpl> Impl_;
};

}  // namespace NKqpRun
