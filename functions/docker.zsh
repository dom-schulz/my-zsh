# Docker Compose utility functions
# Shortcuts for common docker compose workflows

# Docker compose up in detached mode
# Usage: dcud
dcud() {
    docker compose up -d
}

# Docker compose down
# Usage: dcd
dcd() {
    docker compose down
}

# Docker compose down with volumes
# Usage: dcdn
dcdn() {
    echo "⚠️  This will remove volumes"
    read -q "REPLY?Continue? (y/n) "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down -v
    else
        echo "Cancelled"
        return 1
    fi
}

# Docker compose restart service
# Usage: dcr <service>
dcr() {
    if [ -z "$1" ]; then
        echo "ℹ️  No service specified, restarting all services"
        docker compose restart
    else
        docker compose restart "$@"
    fi
}

# Docker compose logs
# Usage: dcl <service>
dcl() {
    if [ -z "$1" ]; then
        docker compose logs
    else
        docker compose logs "$@"
    fi
}

# Docker compose logs follow
# Usage: dclf <service>
dclf() {
    if [ -z "$1" ]; then
        docker compose logs -f
    else
        docker compose logs -f "$@"
    fi
}

# Docker compose ps (list services)
# Usage: dcps
dcps() {
    docker compose ps
}

# Docker compose exec
# Usage: dce <service> <command>
dce() {
    if [ -z "$1" ]; then
        echo "❌ Error: Service name required"
        echo "Usage: dce <service> <command>"
        return 1
    fi
    
    if [ -z "$2" ]; then
        echo "❌ Error: Command required"
        echo "Usage: dce <service> <command>"
        return 1
    fi
    
    docker compose exec "$@"
}

# Docker compose exec bash
# Usage: dceb <service>
dceb() {
    if [ -z "$1" ]; then
        echo "❌ Error: Service name required"
        echo "Usage: dceb <service>"
        return 1
    fi
    
    docker compose exec "$1" bash
}

# Docker compose exec sh (for alpine containers)
# Usage: dces <service>
dces() {
    if [ -z "$1" ]; then
        echo "❌ Error: Service name required"
        echo "Usage: dces <service>"
        return 1
    fi
    
    docker compose exec "$1" sh
}

# Docker compose build
# Usage: dcb
dcb() {
    docker compose build "$@"
}

# Docker compose build no cache
# Usage: dcbn
dcbn() {
    docker compose build --no-cache "$@"
}

# Docker compose pull
# Usage: dcpull
dcpull() {
    docker compose pull
}

# Docker compose stop
# Usage: dcstop
dcstop() {
    if [ -z "$1" ]; then
        docker compose stop
    else
        docker compose stop "$@"
    fi
}

# Docker compose start
# Usage: dcstart
dcstart() {
    if [ -z "$1" ]; then
        docker compose start
    else
        docker compose start "$@"
    fi
}

# Docker compose rm (remove stopped containers)
# Usage: dcrm
dcrm() {
    docker compose rm -f "$@"
}

# Docker compose config (validate and view)
# Usage: dcconfig
dcconfig() {
    docker compose config
}

# Docker compose top (display running processes)
# Usage: dctop
dctop() {
    if [ -z "$1" ]; then
        docker compose top
    else
        docker compose top "$1"
    fi
}

# Docker compose watch (for development)
# Usage: dcwatch
dcwatch() {
    docker compose watch
}

# Docker system prune
# Usage: dprune
dprune() {
    echo "⚠️  This will remove all unused containers, networks, images (dangling), and optionally volumes"
    read -q "REPLY?Continue? (y/n) "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune
    else
        echo "Cancelled"
        return 1
    fi
}

# Docker system prune all (including all unused images)
# Usage: dprunea
dprunea() {
    echo "⚠️  This will remove ALL unused containers, networks, images, and optionally volumes"
    read -q "REPLY?Continue? (y/n) "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -a
    else
        echo "Cancelled"
        return 1
    fi
}

