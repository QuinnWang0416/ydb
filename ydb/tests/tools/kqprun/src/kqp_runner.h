#pragma once

#include "common.h"


namespace NKqpRun {

class TKqpRunner {
public:
    explicit TKqpRunner(const TRunnerOptions& options);

    bool ExecuteSchemeQuery(const TString& query) const;

    bool ExecuteScript(const TString& script, NKikimrKqp::EQueryAction action) const;

    bool WriteScriptResults() const;

private:
    class TImpl;
    std::shared_ptr<TImpl> Impl_;
};

}  // namespace NKqpRun
