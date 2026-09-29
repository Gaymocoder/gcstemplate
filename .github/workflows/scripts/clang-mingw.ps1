$PSNativeCommandUseErrorActionPreference

if ("{gcst::clang_github_ci_full_version}" -eq "latest") {
    $tag = gh release view -R mstorsjo/llvm-mingw --json tagName --jq .tagName
} else {
    $re = "with LLVM $([regex]::Escape("{gcst::clang_github_ci_full_version}"))( final)?$"
    $tag = (
        gh release list -R mstorsjo/llvm-mingw -L 1000 --json tagName,name |
        ConvertFrom-Json |
        Where-Object { $_.name -match $re } |
        Select-Object -First 1
    ).tagName
}

if (-not $tag) {
    throw "No llvm-mingw release with LLVM {gcst::clang_github_ci_full_version}"
}

Invoke-WebRequest "https://github.com/mstorsjo/llvm-mingw/releases/download/$tag/llvm-mingw-$tag-ucrt-x86_64.zip" -OutFile llvm-mingw.zip
tar -xf llvm-mingw.zip -C C:\
"C:\llvm-mingw-$tag-ucrt-x86_64\bin" | Out-File -Append -Encoding utf8 $env:GITHUB_PATH