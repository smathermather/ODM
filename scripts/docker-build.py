#!/usr/bin/env python3
"""Build the runtime ODM Docker image with OCI image labels.

Invoked via `pixi run docker-build` (add `--gpu` for the GPU image, and pass
extra `docker build` flags after `--`). This stamps revision, version and
created labels from the working tree; published images get the equivalent
labels from metadata-action, with the version derived from the git ref there
rather than the VERSION file.
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    p = argparse.ArgumentParser(description="Build the runtime ODM Docker image")
    p.add_argument("--gpu", action="store_true", help="Build the GPU image from gpu.Dockerfile")
    p.add_argument("-t", "--tag", default="", help="Image tag (default: opendronemap/odm:<branch>, or :edge/:edge-gpu on master)")
    return p.parse_known_args()


def git_revision():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip()
    return sha + "-dirty" if dirty else sha


def git_branch():
    try:
        name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT).decode().strip()
    except (subprocess.CalledProcessError, OSError):
        return ""
    return "" if name == "HEAD" else name


def default_tag(gpu, branch):
    # Off master, tag with the branch name; on master, match the tag CI
    # publishes for that ref. :latest and :gpu belong to releases.
    if branch and branch != "master":
        slug = re.sub(r"[^A-Za-z0-9_.-]", "-", branch).lstrip(".-")
        return "opendronemap/odm:%s-gpu" % slug if gpu else "opendronemap/odm:%s" % slug
    return "opendronemap/odm:edge-gpu" if gpu else "opendronemap/odm:edge"


def main():
    args, docker_args = parse_args()

    with open(os.path.join(ROOT, "VERSION")) as f:
        version = f.read().strip()

    dockerfile = "gpu.Dockerfile" if args.gpu else "Dockerfile"
    tag = args.tag or default_tag(args.gpu, git_branch())
    build_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    cmd = [
        "docker", "build",
        "-f", dockerfile,
        "--target", "runtime",
        "-t", tag,
        "--label", "org.opencontainers.image.revision=%s" % git_revision(),
        "--label", "org.opencontainers.image.created=%s" % build_date,
        "--label", "org.opencontainers.image.version=%s" % version,
        *docker_args,
        ".",
    ]
    print(" ".join(cmd))
    sys.exit(subprocess.run(cmd, cwd=ROOT).returncode)


if __name__ == "__main__":
    main()
