#!/usr/bin/env bash
set -e

# ============================================================
#              CONFIGURATION (EDIT THESE ONLY)
# ============================================================
COMPOSE_FILE="docker-compose.yml"
PROJECT_PREFIX="weather-trends"

# ============================================================
#                    HELPER FUNCTIONS
# ============================================================

start_service() {
    echo ""
    echo "============================================"
    echo "       WEATHER TRENDS ANALYZER"
    echo "============================================"
    echo ""
    echo "Starting Docker Compose..."
    docker compose -f "$COMPOSE_FILE" up --build -d

    echo ""
    echo "============================================"
    echo "  Service is running."
    echo ""
    echo "  Charts will be saved to: ./output/"
    echo "============================================"
    return 0
}

remove_images() {
    echo ""
    echo "Removing images..."
    IMAGE_NAME=$(docker compose -f "$COMPOSE_FILE" config --images 2>/dev/null || true)

    if [[ -n "$IMAGE_NAME" ]]; then
        echo "Found image: $IMAGE_NAME"
        docker rmi -f "$IMAGE_NAME" 2>/dev/null || true
    fi

    for IMAGE in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i "$PROJECT_PREFIX"); do
        echo "Found image: $IMAGE"
        docker rmi -f "$IMAGE" 2>/dev/null || true
    done

    echo "Images removed."
}

show_menu() {
    echo ""
    echo "=============================="
    echo "Weather Trends Analyzer"
    echo ""
    echo "  k = stop (keep image)"
    echo "  q = stop + remove image"
    echo "  v = stop + remove image + volumes"
    echo "  r = full restart (stop, remove, rebuild, relaunch)"
    echo "=============================="
}

# ============================================================
#                     START THE SERVICE
# ============================================================

start_service
show_menu

# ============================================================
#                     MAIN LOOP
# ============================================================

while true; do
    read -rp "Enter selection (k/q/v/r): " CHOICE
    CHOICE=$(printf '%s' "$CHOICE" | tr '[:upper:]' '[:lower:]')

    case "$CHOICE" in
        k)
            echo ""
            echo "Stopping containers..."
            docker compose -f "$COMPOSE_FILE" down
            echo "Done."
            exit 0
            ;;
        q)
            echo ""
            echo "Stopping containers..."
            docker compose -f "$COMPOSE_FILE" down --remove-orphans
            remove_images
            echo "Done."
            exit 0
            ;;
        v)
            echo ""
            echo "Stopping containers and removing volumes..."
            docker compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
            remove_images
            echo "Done."
            exit 0
            ;;
        r)
            echo ""
            echo "=== FULL RESTART ==="
            echo "Stopping containers..."
            docker compose -f "$COMPOSE_FILE" down --remove-orphans
            remove_images
            echo ""
            start_service
            show_menu
            ;;
        *)
            echo "Invalid selection. Enter k, q, v, or r."
            ;;
    esac
done