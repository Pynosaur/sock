genrule(
    name = "sock_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]),
    outs = ["sock"],
    cmd = """
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-sock \
            --no-progressbar \
            --assume-yes-for-downloads \
            --no-deployment-flag=self-execution \
            --output-dir=$$(dirname $(location sock)) \
            --output-filename=sock \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)

