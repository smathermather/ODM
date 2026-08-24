# Releasing ODM

This document describes how a versioned ODM release is produced and how to
verify that every artifact actually shipped.

## What a release produces

A release is cut by pushing a `v<version>` git tag (e.g. `v3.6.1`). Three
workflows react to the tag:

| Workflow | File | Artifact | Destination |
| --- | --- | --- | --- |
| Publish Windows Setup | `.github/workflows/publish-windows.yml` | `ODM_Setup_<version>.exe` (signed) | Attached to the GitHub Release |
| Docker CPU Image | `.github/workflows/docker.yaml` | `opendronemap/odm:<version>` and `:latest` | Docker Hub |
| Docker GPU Image | `.github/workflows/docker-gpu.yaml` | `opendronemap/odm:<version>-gpu` and `:gpu` | Docker Hub |

The **only** asset attached to the GitHub Release object is the Windows
installer. The Docker images are pushed to Docker Hub, not to the release.

## Docker tags

| Tag | Written by | Meaning |
| --- | --- | --- |
| `opendronemap/odm:edge` | master push | latest master build |
| `opendronemap/odm:edge-gpu` | master push | latest master GPU build |
| `opendronemap/odm:latest` | `v*` tag | newest stable release |
| `opendronemap/odm:<version>` | `v*` tag | that release |
| `opendronemap/odm:<version>-gpu` | `v*` tag | that GPU release |
| `opendronemap/odm:gpu` | `v*` tag | alias of the newest `<version>-gpu` |

A master push updates `:edge` and `:edge-gpu` and touches nothing else, so
`:latest` never moves between releases.

## How the Docker images are built

Both Docker workflows derive their tags from the git ref with
`docker/metadata-action`: a master push produces the `edge` tags, a `v*` tag
produces the versioned tags plus `:latest` (CPU) and `:gpu` (GPU). A release
is a fresh build of the tagged commit by the same workflow that builds master,
not a copy of the master image. `pixi.lock` pins the toolchain and library
dependencies; the Ubuntu base image and apt packages resolve at build time.

The CPU workflow delegates the build to Docker's `github-builder` reusable
workflow (`docker/github-builder/.github/workflows/build.yml`): each platform
builds on its own native GitHub-hosted runner and the results are assembled
into one multi-arch manifest, with signed SLSA provenance attached. The
`cosign` commands to verify a build's signature are available from the
workflow run's outputs. The GPU workflow builds on a hosted runner after
clearing the preinstalled toolchains its image needs the disk for.

## Pre-flight checklist

- [ ] `VERSION` on the release commit matches the tag you are about to push.
      It sets the installer filename and the version ODM reports at runtime.
      Docker image tags and the `org.opencontainers.image.version` label both
      come from the git tag.
- [ ] The latest `master` runs of all three workflows above are green on
      the release commit. A tag build reuses the same steps, so a green master
      build is the best predictor that the tagged build will succeed.

Do not tag until the master builds are green. Tagging a broken `master`
reproduces the broken build against the tag and yields a release with missing
artifacts.

## Cutting the release

1. Merge the release commit (with the bumped `VERSION`) to `master` and wait
   for all three workflows to go green on that commit.
2. Create the GitHub Release and its `v<version>` tag pointing at that commit.
   `svenstaro/upload-release-action` will also create the release if it does
   not already exist, but creating it up front lets you write the changelog.
3. The tag push triggers all three workflows again. The Windows and GPU
   builds are the longest.

## Post-release verification

- [ ] `gh release view v<version> --json assets` lists `ODM_Setup_<version>.exe`.
- [ ] `docker buildx imagetools inspect opendronemap/odm:<version>` succeeds
      and lists both `linux/amd64` and `linux/arm64`.
- [ ] `opendronemap/odm:latest` and `:<version>` resolve to the same digest;
      `:gpu` and `:<version>-gpu` resolve to the same digest.
- [ ] All three tag-triggered workflow runs concluded with `success`.

A failed tag workflow is recovered by fixing the cause and re-running that
workflow run; the tag does not need to be recreated.

## NodeODM

The publish workflows no longer dispatch NodeODM rebuilds: NodeODM's images
assume the pre-pixi filesystem layout and cannot build on the current base
image. Until NodeODM supports the pixi layout, its images are rebuilt
manually.
