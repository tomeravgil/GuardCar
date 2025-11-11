#!/bin/bash
set -e

# Wait until RabbitMQ fully starts
rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit@$(hostname).pid

# Create user (no error if already exists)
rabbitmqctl add_user "$RABBITMQ_DEFAULT_USER" "$RABBITMQ_DEFAULT_PASS" || true

# Create vhost
rabbitmqctl add_vhost "$RABBITMQ_DEFAULT_VHOST" || true

# Give user full permissions
rabbitmqctl set_permissions -p "$RABBITMQ_DEFAULT_VHOST" "$RABBITMQ_DEFAULT_USER" ".*" ".*" ".*"

echo "RabbitMQ user+vhost+permissions configured"
