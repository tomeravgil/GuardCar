import pika
import json
import sys

AMQP_URL = "amqp://guest:guest@localhost:5672/"

connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
channel = connection.channel()

def publish(queue, message):
    payload = json.dumps(message).encode()
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=payload
    )
    print(f"[OK] Published → {queue}: {payload}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python publish_test_message.py <queue> <json>")
        print('Example:')
        print(' python publish_test_message.py CLOUD_PROVIDER_CONFIG_QUEUE \'{"connection_ip":"10.0.0.1:50051","server_certification":"cert.pem","delete":false}\'')
        sys.exit(1)

    queue = sys.argv[1]

    new = '{"connection_ip":"0.0.0.0:50051","server_certification":"MIIFmzCCA4OgAwIBAgIUAsDE4ZJsCp+PbSZFuJ+9M6jiNOUwDQYJKoZIhvcNAQELBQAwXTELMAkGA1UEBhMCVVMxEzARBgNVBAgMCkNhbGlmb3JuaWExEjAQBgNVBAcMCVNhbiBEaWVnbzERMA8GA1UECgwIR3VhcmRDYXIxEjAQBgNVBAMMCWxvY2FsaG9zdDAeFw0yNTExMjExNzE3MzFaFw0yNjExMjExNzE3MzFaMF0xCzAJBgNVBAYTAlVTMRMwEQYDVQQIDApDYWxpZm9ybmlhMRIwEAYDVQQHDAlTYW4gRGllZ28xETAPBgNVBAoMCEd1YXJkQ2FyMRIwEAYDVQQDDAlsb2NhbGhvc3QwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDahLF8a+Fi6AMoKQ87aNNJQV5CJUjzK2BxfZcknJCXZKRX0JCuzimcWlb+ncGK4e4HCcz+CUzBJB2EkObk4xkjJmf8AeJ1ZbaFekApbZUwDCGVxfugFWDO8fuNFDFQ6M+NfuAl3zri9yh2x6UbfLUaCWRmhYMwq7GfIleVvBkDROUpCtOQKKaMbbuVeGqqHeuk4Fhs6vp7x3wyo0K5zIchZq4Jw5gdYjfmtIhllImY3/s6l27i8AkA2rF3uYUMBaJImLKsxqnVNnJE937wUW05zzjBlxHC2nQkp64ak+3aNBr690q+CbiorGLTXSmPxXRrLNl3nsQOmzydIKzq1bl9xYFAEArez1dCnkBidCKv1/Rp3X6nTISmZN/1d/MMF1A1zaLud3nPnU+WlGEuN+k8RnPlTMpkmkV0/iD3ffpr5EqVMx+2RtBWErr/pKHitygkSeQOI6t+4B8lNps80mYOrscZCVmc0nrh2FvczgW0+5IetQJvbgGczLdVjFUhGQcHwCok7cXRafPeQ20zVEWd7yl256KssV6vhGJCMMvujYSC+OcvUAjuovIgUi+N0CXk9mRJAnb67cAIz3dGykwqk1XtS8GTvVog35lxCWkBkuXnviPX54h9dLnen4OA36da1NBvTf+MfCm5DVhs1jLyhYMe5XKpShc3JBLCWWL7nwIDAQABo1MwUTAdBgNVHQ4EFgQU+kxL0ptRcMzCTyBjqOM03t3myoswHwYDVR0jBBgwFoAU+kxL0ptRcMzCTyBjqOM03t3myoswDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEARrQtWAeUavduZQRC0pkqBSD+3KaqukCtBQnqQOZWwBpdsStYFs6iWTkTvT2e4Q57MC2Ypn5cfiz2evG9DOojSCMLw1mcf0UOW8pkxw/q8lkhNVtoV932LzHgMUFANLTZC/QHco4Ry0FeuqRbxeAloxDIm7TkrTY8GJR6HtAKd8/3l3ClaAezfr5s1hRVAliAZhjNSr8G8Bj+eJgg1B/6v7FyBxfBKTkv3HZV6PjH/BzHfdyqPbhcQQlH+rCcQOLh9lSNWeGXVZ8b2GjlEth29c1I9zK0TC9ca6sqCvjuDIUtSszTFSd0mhbUG1KbEdT9k4aM7HeF97qXldne5F5HANUS+Gl1toDWU6aTsFOdGyEReu0dE/juH2T9GWgeml7ZQBFLe/ARIlzRB2loRQ/yPyPvj7o+eXbNv2CADxKOTPJ7pjiV7ve/HqgyvnYmiZHtSWBmwfIBUwxz6T0Lt4ULx6Ue2PhpBXS8v1oraM9/9ZnHyL1yjJgJGv5ZaD83oSYTQFklK7NdMqCUKw142cta8vkAGG4PpeeYtXF85I1aohUo9pn7yzkp3s8zM1/amlLPOhlZqq45UAFgNMk8+xP/2j8Z+XN+bAHryNjIsmVlYSqmnpGwEHkaCoRV8hlfH4DX9f95GpqFXu00hF+96zKGaoYwqIpgggdkU3QJViAsWgo=","delete":false}'
    message = json.loads(new)
    publish(queue, message)

    connection.close()
