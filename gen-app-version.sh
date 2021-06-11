#!/bin/bash
arrIN=(${GITHUB_REF//\// })
branch_name=arrIN[-1]
echo $branch_name-$GITHUB_RUN_NUMBER
