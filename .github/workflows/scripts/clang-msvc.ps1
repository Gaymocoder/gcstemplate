$PSNativeCommandUseErrorActionPreference = $true

if ("{gcst::clang_full_version_github_ci}" -eq "latest") {
    $tag = gh release view -R llvm/llvm-project --json tagName --jq .tagName
} else {
    $tag = "llvmorg-{gcst::clang_full_version_github_ci}"
}
$ver  = $tag -replace '^llvmorg-', ''
$name = "clang+llvm-$ver-x86_64-pc-windows-msvc"

Invoke-WebRequest "https://github.com/llvm/llvm-project/releases/download/$tag/$name.tar.xz" -OutFile llvm.tar.xz
cmd /c "7z x llvm.tar.xz -so | 7z x -si -ttar -oC:\ -y"
Move-Item "C:\$name" C:\LLVM
"C:\LLVM\bin" | Out-File -Append -Encoding utf8 $env:GITHUB_PATH