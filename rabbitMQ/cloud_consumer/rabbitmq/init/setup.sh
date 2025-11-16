#!/bin/bash
set -e

# Wait for RabbitMQ to fully start
rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit@$(hostname).pid

echo "[Init] Configuring default user + vhost..."

# Create default user (from env vars)
rabbitmqctl add_user "$RABBITMQ_DEFAULT_USER" "$RABBITMQ_DEFAULT_PASS" || true

# Create default vhost
rabbitmqctl add_vhost "$RABBITMQ_DEFAULT_VHOST" || true

# Grant permissions to default user
rabbitmqctl set_permissions -p "$RABBITMQ_DEFAULT_VHOST" "$RABBITMQ_DEFAULT_USER" ".*" ".*" ".*"

echo "[Init] Default user/vhost configured."

###########################################################################
# Create GUARD CAR user (you requested this)
###########################################################################

GUARD_USER="guardcar"
GUARD_PASS="guardcar"

echo "[Init] Creating GuardCar user..."

# Create user (ignore error if it exists)
rabbitmqctl add_user "$GUARD_USER" "$GUARD_PASS" || true

# Give full permissions to GuardCar user
rabbitmqctl set_permissions -p "$RABBITMQ_DEFAULT_VHOST" "$GUARD_USER" ".*" ".*" ".*"

# Optional: tag as administrator
rabbitmqctl set_user_tags "$GUARD_USER" administrator || true

echo "[Init] GuardCar user created with full permissions."

echo "[Init] Done."
