sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install -y g++-{gcst::gcc_major_version_github_ci}
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-{gcst::gcc_major_version_github_ci} 100
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-{gcst::gcc_major_version_github_ci} 100