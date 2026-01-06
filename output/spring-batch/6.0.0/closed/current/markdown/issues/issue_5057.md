# `CommandLineJobOperator` improve state validation for restart/abandon and enhance logging

**Issue番号**: #5057

**状態**: closed | **作成者**: ch200203 | **作成日**: 2025-10-29

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5057

## 内容


### Expected Behavior
- **Abandon**: Only allow when execution is **STOPPED**; otherwise log the current status and return a generic error exit code.
- **Restart**: Only allow when execution is **FAILED** or **STOPPED**; otherwise log the current status and return a generic error exit code.
- Resolve the TODOs in `CommandLineJobOperator` by performing explicit precondition checks at the CLI layer without relying on deprecated exceptions.

### Current Behavior
- `abandon(jobExecutionId)`: Delegates to `JobOperator#abandon` without enforcing **STOPPED** at the CLI level. A TODO mentions throwing `JobExecutionNotStoppedException`, but that exception is deprecated.
- `restart(jobExecutionId)`: Contains a TODO to check/log when the job execution “did not fail,” but does not enforce valid restart states at the CLI level.

### Context
- **Motivation**: Align CLI precondition checks with Spring Batch semantics and the inline TODOs, prevent invalid operations earlier, and improve observability with clear error logs that include the current status.
- **Alternative considered**: Throwing `JobExecutionNotStoppedException`, but it is deprecated; the CLI should use exit codes and logging instead.
- **Compatibility**: No API change; behavior becomes explicit and predictable. Invalid operations return `JVM_EXITCODE_GENERIC_ERROR` rather than relying on downstream exceptions.

### Proposed Change
- In `spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/CommandLineJobOperator.java`:
    - `restart(long jobExecutionId)`: Enforce `FAILED` or `STOPPED`; otherwise log current status and return generic error.
    - `abandon(long jobExecutionId)`: Enforce `STOPPED`; otherwise log current status and return generic error.

### Previous Code (before change)
- `restart(long jobExecutionId)`: Only TODO present; no state check; directly delegates to `jobOperator.restart(jobExecution)`.

```java
// TODO should check and log error if the job execution did not fail
JobExecution restartedExecution = this.jobOperator.restart(jobExecution);
return this.exitCodeMapper.intValue(restartedExecution.getExitStatus().getExitCode());
```

- `abandon(long jobExecutionId)`: Only TODO present; no state check; directly delegates to `jobOperator.abandon(jobExecution)`.

```java
// TODO should throw JobExecutionNotStoppedException if the job execution is
// not stopped
JobExecution abandonedExecution = this.jobOperator.abandon(jobExecution);
return this.exitCodeMapper.intValue(abandonedExecution.getExitStatus().getExitCode());
```

A corresponding pull request has been carefully prepared to demonstrate this improvement.  
I would appreciate it if the team could review and provide feedback when possible.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

Resolved with #5058

