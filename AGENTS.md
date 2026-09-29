# AGENTS.md

This file guides Codex when working with code in this repository.

## Project Overview

godzilla is MOOSE application where we are developing a dislocation density based crystal plasticity for thermal creep for cladding material 316L.

- Phenomonological Crystal Plasticity (Already implemented within the MOOSE framework)
- Define a dislocation glide and climb based crystal plasticity materials.
- Build on top of the present Crystal Plasticity framework.


## Architecture

### Application Codebase

The custom C++ scripts for kernels and material models are to be defined in the following directories:

```text
 godzilla/ 
├── include/ 
│ ├── base/ 
│ ├── kernels/ <! -- C++ header file for kernels -->
│ └── materials/ <! -- C++ header file for materials -->
└── src/
│ ├── base/ 
│ ├── kernels/ <! -- C++ script (.C) for kernels -->
│ └── materials/ <! -- C++ script (.C) for materials -->
 ```
### MOOSE framework codebase

The moose framework codebase is located in the following path:

```text
/home/ghostrobot96/projects/moose
 ```
This path can be used for application development reference as MOOSE framework has preimplemented kernels, materials and many other features. It is useful for both application development and verification purpose.

### References

This directory contains some references in the form of markdown file or papers in pdf format, which will be helpful in the development phase.

path:

```text
/home/ghostrobot96/projects/godzilla/references/
 ```

Use the official documentation of MOOSE first and then github discussions for reference.

## Code style

Refer to the guidelines mentioned in the url given below:

```text
https://mooseframework.inl.gov/sqa/framework_scs.html
 ```

## Boundaries

- Do not modify the files from the MOOSE framework codebase.
- Only write/ modify scripts in the Application codebase.
- Create input files (.i) file in the base directory.

## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.