#!/usr/bin/env python3
"""
RF-DETR Consumer Service

This script runs the RF-DETR consumer that processes messages from a RabbitMQ queue.
It can be configured using command-line arguments or environment variables.

Environment Variables:
    RABBITMQ_HOST: RabbitMQ server host (default: localhost)
    RABBITMQ_PORT: RabbitMQ server port (default: 5672)
    RABBITMQ_VHOST: RabbitMQ virtual host (default: /)
    RABBITMQ_USER: RabbitMQ username (default: guest)
    RABBITMQ_PASS: RabbitMQ password (default: guest)

Example:
    # Using environment variables
    export RABBITMQ_HOST=rabbit.example.com
    export RABBITMQ_USER=user
    export RABBITMQ_PASS=pass
    python run_rfdetr_consumer.py

    # Using command-line arguments
    python run_rfdetr_consumer.py --host rabbit.example.com --user user --password pass
"""

import os
import sys
import logging
import argparse
import pika
from pathlib import Path
from detection.model.rf_detr.rf_detr_consumer import RFDETRConsumer
from detection.model.rf_detr.rf_detection import RFDETRDetectionService

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run RF-DETR Consumer Service')
    parser.add_argument('--host', default=os.getenv('RABBITMQ_HOST', 'localhost'),
                      help='RabbitMQ host (default: localhost)')
    parser.add_argument('--port', type=int, default=int(os.getenv('RABBITMQ_PORT', '5672')),
                      help='RabbitMQ port (default: 5672)')
    parser.add_argument('--vhost', default=os.getenv('RABBITMQ_VHOST', '/'),
                      help='RabbitMQ virtual host (default: /)')
    parser.add_argument('--user', default=os.getenv('RABBITMQ_USER', 'guest'),
                      help='RabbitMQ username (default: guest)')
    parser.add_argument('--password', default=os.getenv('RABBITMQ_PASS', 'guest'),
                      help='RabbitMQ password (default: guest)')
    parser.add_argument('--log-level', default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level (default: INFO)')
    return parser.parse_args()

def setup_logging(level='INFO'):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function to run the RF-DETR consumer."""
    args = parse_args()
    logger = setup_logging(args.log_level)
    
    logger.info("Starting RF-DETR Consumer Service")
    logger.info(f"Connecting to RabbitMQ at {args.host}:{args.port}{args.vhost} as {args.user}")
    try:
        detection_service = RFDETRDetectionService("rfdetr-nano")
        # Initialize and start consumer
        consumer = RFDETRConsumer(
            user=args.user,
            password=args.password,
            host=args.host,
            vhost=args.vhost,
            rf_detection_service=detection_service
        )
        
        # Connect to RabbitMQ
        consumer.connect()
        logger.info("Connected to RabbitMQ. Waiting for messages...")
        
        # Start consuming messages
        consumer.start()
        
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        sys.exit(1)
    finally:
        if 'consumer' in locals() and hasattr(consumer, 'connection') and consumer.connection.is_open:
            consumer.connection.close()
        logger.info("RF-DETR Consumer Service stopped")

if __name__ == "__main__":
    main()
