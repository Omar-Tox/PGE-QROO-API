FROM php:8.3-fpm

# Install dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    git \
    unzip \
    libpq-dev \
    && docker-php-ext-install pdo pdo_pgsql

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy project
COPY . .

# Install Laravel dependencies
RUN composer install --no-dev --optimize-autoloader

# === ¡AQUÍ ESTÁ LA CORRECCIÓN! ===
# Cambia el propietario de TODOS los archivos a www-data
RUN chown -R www-data:www-data /var/www/html

# Esta línea también es buena, pero la de arriba es más completa
# RUN chown -R www-data:www-data storage bootstrap/cache

RUN apt-get update && apt-get install -y procps

# Copy nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Establece los permisos correctos para Laravel
RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache
RUN chmod -R 775 /var/www/html/storage /var/www/html/bootstrap/cache

# Start nginx and PHP-FPM together
CMD php-fpm & nginx -g 'daemon off;'