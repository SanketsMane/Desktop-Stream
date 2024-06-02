from pyngrok import ngrok

# [<NgrokTunnel: "https://<public_sub>.ngrok.io" -> "http://localhost:80">]
tunnels = ngrok.get_tunnels()