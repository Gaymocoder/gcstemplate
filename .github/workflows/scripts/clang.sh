wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh {gcst::clang_github_ci_major_version} all
sudo apt update
sudo apt install -y libc++-{gcst::clang_github_ci_major_version}-dev libc++abi-{gcst::clang_github_ci_major_version}-dev

sudo update-alternatives --install /usr/bin/clang   clang   /usr/bin/clang-{gcst::clang_github_ci_major_version}   1000
sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-{gcst::clang_github_ci_major_version} 1000
sudo update-alternatives --set clang   /usr/bin/clang-{gcst::clang_github_ci_major_version}
sudo update-alternatives --set clang++ /usr/bin/clang++-{gcst::clang_github_ci_major_version}
clang --version