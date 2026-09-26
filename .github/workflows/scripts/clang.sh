wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh {gcst::clang_major_version_github_ci} all
sudo apt update
sudo apt install -y libc++-{gcst::clang_major_version_github_ci}-dev libc++abi-{gcst::clang_major_version_github_ci}-dev

sudo update-alternatives --install /usr/bin/clang   clang   /usr/bin/clang-{gcst::clang_major_version_github_ci}   1000
sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-{gcst::clang_major_version_github_ci} 1000
sudo update-alternatives --set clang   /usr/bin/clang-{gcst::clang_major_version_github_ci}
sudo update-alternatives --set clang++ /usr/bin/clang++-{gcst::clang_major_version_github_ci}
clang --version