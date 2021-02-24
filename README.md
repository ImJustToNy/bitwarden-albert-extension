# ![Bitwarden logo](https://raw.githubusercontent.com/bitwarden/brand/master/icons/32x32.png) Bitwarden Albert Extension
![Example](https://user-images.githubusercontent.com/5730766/108998107-b648c780-76a0-11eb-8eed-3fd4b260340e.png)

# How to install
1. Clone extension repo:

`git clone https://github.com/ImJustToNy/bitwarden-albert-extension ~/.local/share/albert/org.albert.extension.python/modules/Bitwarden`

2. [Install 'bw', official CLI client for Bitwarden.](https://bitwarden.com/help/article/cli/#download-and-install)
3. Use `bwlogin` expression in Albert to initalise auth process. If you already have your login token, you may use `bwtoken (token)`.

# How to use
Just invoke `bw` along with search query to search your Bitwarden vault. Eg. `bw facebook`. If you wish to see alternative options to copying password, just hold down ALT key. You will have ability to copy username or TOTP.

*This extension was inspired by https://github.com/davidpicarra/lastpass-albert-extension*