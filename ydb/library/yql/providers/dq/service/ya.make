LIBRARY()

SRCS(
    grpc_service.cpp
    grpc_session.cpp
    service_node.cpp
    interconnect_helpers.cpp
)

PEERDIR(
    library/cpp/actors/core
    library/cpp/actors/dnsresolver
    library/cpp/actors/interconnect
    library/cpp/build_info
    library/cpp/grpc/server
    library/cpp/grpc/server/actors
    library/cpp/svnversion
    library/cpp/threading/future
    ydb/library/yql/sql
    ydb/public/api/protos
    ydb/library/yql/providers/common/metrics
    ydb/library/yql/providers/dq/actors
    ydb/library/yql/providers/dq/api/grpc
    ydb/library/yql/providers/dq/common
    ydb/library/yql/providers/dq/counters
    ydb/library/yql/providers/dq/interface
    ydb/library/yql/providers/dq/worker_manager
    ydb/library/yql/providers/dq/worker_manager/interface
)

YQL_LAST_ABI_VERSION()

END()
