<!--
Sync Impact Report
Version change: 2.0.0 -> 2.1.0
Modified principles:
- II. Testing Proves Behavior -> III. Testing Proves Behavior
- III. Consistent User Experience -> IV. Consistent User Experience
- IV. Simplicity and Maintainability -> V. Simplicity and Maintainability
Added sections:
- II. Source Structure Communicates Intent
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md (reviewed; no changes required)
- ✅ .specify/templates/tasks-template.md
- ⚠ .specify/templates/commands/*.md (directory not present)
- ✅ AGENTS.md (reviewed; no changes required)
Follow-up TODOs:
- None
-->
# Pink Noise Constitution

## Core Principles

### I. Code Quality Is a Gate
All production code MUST be clear, cohesive, typed or otherwise validated where the
chosen stack supports it, and consistent with the surrounding architecture. Every
change MUST pass the repository's formatter, linter, static checks, and review before
merge. New abstractions MUST remove real duplication or isolate a concrete domain
boundary; organizational-only abstractions are not acceptable. Rationale: readable,
locally consistent code keeps future changes cheaper than the feature being added.

### II. Source Structure Communicates Intent
Source layout MUST make the primary entry point, orchestration boundary, domain
rules, technical infrastructure, and user-facing output responsibilities easy to
identify from paths alone. Plans MUST document the selected source tree and explain
why each top-level or package-level grouping exists. CLI adapters, application
orchestrators, domain models/rules, infrastructure implementations, and output
rendering MUST remain separate when those responsibilities change for different
reasons. New folders MUST be shallow and responsibility-based; avoid framework,
layer, or pattern names unless they match the project's real vocabulary and reduce
navigation cost. Rationale: source structure is part of the product's maintainable
interface for contributors and should reduce the time required to make safe changes.

### III. Testing Proves Behavior
Behavioral changes MUST include automated tests at the lowest useful level and at
least one user-story or integration-level verification when behavior crosses module,
service, storage, or UI boundaries. Tests MUST be specified before implementation
tasks and MUST fail for the intended reason before the implementation is considered
complete. Bug fixes MUST add a regression test that fails without the fix. Rationale:
tests are the executable contract that protects code quality and safe refactoring.

### IV. Consistent User Experience
User-facing work MUST follow existing interaction patterns, layout conventions,
terminology, accessibility expectations, and visual component choices. Specifications
MUST define the primary user journey, error states, empty states, loading states, and
success criteria for any visible workflow. New UI patterns require documented
justification and a migration plan for affected adjacent surfaces. Rationale: users
experience the product as one system, not as isolated implementation slices.

### V. Simplicity and Maintainability
Solutions MUST choose the smallest design that satisfies the current specification,
keeps ownership boundaries explicit, and leaves the system easier to operate and
change. Shared contracts, schemas, and public interfaces MUST be documented where
introduced or changed. Complexity, new dependencies, and cross-cutting behavior MUST
be justified in the plan's complexity tracking. Rationale: unnecessary complexity is
a long-term cost paid by every later feature.

## Engineering Standards

- Specifications MUST include measurable success criteria, UX consistency
  requirements for user-facing work, and clear acceptance criteria.
- Plans MUST document the selected project structure, responsibility boundaries,
  testing strategy, quality checks, and any constitutional exceptions.
- Tasks MUST include automated test work, quality-check work, and UX validation work
  before a feature can be marked complete.
- Tasks that create or move source files MUST follow the approved plan structure and
  preserve the documented entry point, orchestration, domain, infrastructure, and
  output boundaries.
- Public behavior changes MUST update relevant contracts, examples, or runtime
  documentation in the same change set.
- Dependencies MUST be necessary, maintained, and aligned with existing project
  choices; new dependencies require plan-level rationale.

## Delivery Workflow and Quality Gates

1. A feature specification MUST define independently testable user stories and
   measurable outcomes before planning begins.
2. The implementation plan MUST pass the Constitution Check before research starts
   and again after design artifacts are created.
3. Task generation MUST preserve test-first ordering: tests and validation tasks
   precede implementation tasks for each user story.
4. Implementation is complete only when tests, linting/formatting/static checks,
   and UX acceptance checks relevant to the feature have passed.
5. Any constitutional exception MUST be documented with rationale, a simpler
   alternative considered, an owner, and an expiration or follow-up task.

## Governance

This constitution supersedes conflicting project practices and templates. Amendments
MUST be proposed with a documented rationale, expected impact, affected templates,
and migration notes for active features. Approval requires project maintainer review
and updates to all dependent Spec Kit templates in the same change.

Versioning follows semantic versioning:
- MAJOR for removing or redefining principles in a backward-incompatible way.
- MINOR for adding principles, sections, or materially expanding governance.
- PATCH for clarifications, typo fixes, and non-semantic refinements.

Compliance review is required at plan creation, after design, before implementation
completion, and during review of any change that modifies behavior, templates, or
public contracts.

**Version**: 2.1.0 | **Ratified**: 2026-06-18 | **Last Amended**: 2026-06-18
