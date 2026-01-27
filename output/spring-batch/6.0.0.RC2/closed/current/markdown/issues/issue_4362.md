# Incorrect Step status in StepExecutionListener#afterStep

**Issue番号**: #4362

**状態**: closed | **作成者**: cezarykluczynski | **作成日**: 2023-05-01

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4362

**関連リンク**:
- Commits:
  - [36068b5](https://github.com/spring-projects/spring-batch/commit/36068b5db84ff242032e9b00515454a84e0745d2)
  - [db6ef7b](https://github.com/spring-projects/spring-batch/commit/db6ef7b067e0daeee59c1baea03a0acfed4f5cfc)

## 内容

I'm looking for a way to execute a callback when step is completed. `StepExecutionListener` does not work, because in `afterStep`, step is not acutally completed yet, because it's exit status can still be changed, and status in the DB table is not COMPLETED, but STARTED. 

I'm looking for a way to do it, because after every step, I want to fire an automatic backup of a completed step. For that, it is required that all steps are completed, because if state is later recreated from this backup, Spring Batch would not process further.

I haven't found any way to do it in a clean manner. There is no listener that will execute after one step is completed, but next step is not yet started. If there is one, please point me out, and otherwise, would you consider adding a listener like that? I could probably try and make the PR if this feature is accepted.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2023-06-15

Thank you for opening this issue.

> `StepExecutionListener` does not work, because in `afterStep`, step is not acutally completed yet, because it's exit status can still be changed, and status in the DB table is not COMPLETED, but STARTED.

The issue is with the current implementation of that callback listener in Spring Batch, which is incorrect. According to the contract of that method which states that that method is `Called after execution of the step's processing logic (whether successful or failed)`, the status (both in memory and in the DB) should not be `STARTED` at that point, but rather a non-running status. The end time should be set at that point as well (as reported in #3846). So I believe this is a bug and not a feature that should be requested.

Once this is fixed, I think you can implement your requirement with a `StepExecutionListener`. Do you agree?

### コメント 2 by cezarykluczynski

**作成日**: 2023-06-22

@fmbenhassine Yes, if status was non-running in both memory and DB, that would solve my problem. However, the `afterStep` method returns `an {@link ExitStatus} to combine with the normal value`, which gives the chance to overwrite the original exit status. Therefore, if non-null status is returned, one more save in the `AbstractStep` around line 268 is needed (hopefully it's that simple). I'm also not sure if that would not break some assumptions other people are making about how Spring Batch works here, even if they rely on a bug.

### コメント 3 by gdupontf

**作成日**: 2023-08-16

Forgive me if I'm wrong, but isn't the same problem present at the job level?
I had the same behaviour using `JobExecutionListener`s.

### コメント 4 by fmbenhassine

**作成日**: 2025-11-03

> Yes, if status was non-running in both memory and DB, that would solve my problem

@cezarykluczynski the step execution status is now persisted before calling listeners, so it should be seen as a non-running status in both memory and job repository (even though I believe one should not query the job repository at that point, but only use the reference to the step execution that the listener provides).

That said, in hindsight, I don't understand why `afterStep` returns an `ExitStatus`.. The javadoc mentions to "give a listener a chance to modify the exit status from a step"  but I don't see any use case for that (I might be missing something). I personally never used that "feature". Moreover, this is not consistent with `JobExecutionListener#afterJob` which returns `void` and not an `ExitStatus`. Why is one able to change the step's execution status in `StepExecutionListener#afterStep`, but is not able to change the job's execution status in `JobExecutionListener#afterJob` ?

Unless there is a good reason / use case for that, I believe that that method should be deprecated and replaced with one that returns `void`. I opened #5074 to discuss this and gather feedback, so please share your thoughts there. Many thanks upfront.

@gdupontf 

> Forgive me if I'm wrong, but isn't the same problem present at the job level? I had the same behaviour using JobExecutionListeners.

You are right, I fixed that for job listeners as well, 36068b5db84ff242032e9b00515454a84e0745d2.


