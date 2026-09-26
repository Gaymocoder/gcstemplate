$PSNativeCommandUseErrorActionPreference = $true

choco install mingw --version={gcst::gcc_full_version_github_ci} -y
echo "C:\ProgramData\mingw64\mingw64\bin" >> $env:GITHUB_PATH