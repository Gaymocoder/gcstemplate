$PSNativeCommandUseErrorActionPreference = $true

choco install mingw --version={gcst::gcc_github_ci_full_version} -y
echo "C:\ProgramData\mingw64\mingw64\bin" >> $env:GITHUB_PATH