# Certs Set up
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout VideoContainer/Sender/key.pem \
  -out VideoContainer/Sender/cert.pem \
  -subj "/CN=$(hostname)"
chmod 600 VideoContainer/Sender/key.pem