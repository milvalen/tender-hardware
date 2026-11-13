# Working rules

- This repository is public. Never commit secrets or personal data. Read keys from the environment or from `../keys/`.
- Do not reference other companies' games, brands or artists in models, renders or docs. Follow the Ink Industrial design language in `tender-vault/10-concept/design-language.md`.
- The enclosure is code: change the build123d source, not exported meshes. Commit STEP/STL exports only for tagged releases.
- Write code, identifiers, comments, commit messages and every `README.md` in English only. Stencil markings on the enclosure (`UNIT TND-01`, `TBL-07`) are product content.
- Documentation lives in the `tender-vault` repository. Do not copy it here.
- The default branch is `dev`. `main` is the release branch and is never ahead of `dev`. Agents work in `ai/<area>` branches. When the work is ready, the agent merges `ai/<area>` into `feature/<area>` (created from `dev` if it does not exist) and pushes both. Artemy Erkov reviews the result on `feature/<area>` and accepts it. After acceptance, the agent merges `feature/<area>` into `dev` on Artemy's command.
- `dev` goes to `main` only after Artemy Erkov carefully reviews `dev` and gives the command.
- Exception: changes to working rules only (`CLAUDE.md`, branch and process rules) go straight into `dev`, without a `feature/<area>` review.
- The vault records the state of `dev`: when a vault page describes this repository, it describes what is in `dev`, not what is only on `ai/*` or `feature/*`.
- Do not rewrite commit history.
