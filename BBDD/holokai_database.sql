-- =========
-- 1. USERS
-- =========
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    first_name VARCHAR(80),
    last_name VARCHAR(120),
    email VARCHAR(190),
    password_hash VARCHAR(255),
    phone VARCHAR(25),
    avatar_url VARCHAR(500),
    role ENUM('CUSTOMER', 'ADMIN') DEFAULT 'CUSTOMER',
    status ENUM('ACTIVE', 'INACTIVE', 'BLOCKED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_users_id PRIMARY KEY (id),

    CONSTRAINT nn_users_first_name CHECK (first_name IS NOT NULL),
    CONSTRAINT nn_users_email CHECK (email IS NOT NULL),
    CONSTRAINT nn_users_password_hash CHECK (password_hash IS NOT NULL),
    CONSTRAINT nn_users_role CHECK (role IS NOT NULL),
    CONSTRAINT nn_users_status CHECK (status IS NOT NULL),

    CONSTRAINT uk_users_email UNIQUE (email),

    CONSTRAINT chk_users_role CHECK (role IN ('CUSTOMER', 'ADMIN')),
    CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'BLOCKED')
    )
) ENGINE=InnoDB;


-- ==============
-- 2. DIRECCIONES
-- ==============
CREATE TABLE addresses (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    user_id BIGINT UNSIGNED,
    recipient_name VARCHAR(160),
    phone VARCHAR(25),
    street VARCHAR(220),
    city VARCHAR(100),
    postal_code VARCHAR(15),
    province VARCHAR(100),
    country VARCHAR(100) DEFAULT 'España',
    is_default BOOLEAN DEFAULT FALSE,

    default_user_id BIGINT UNSIGNED
        GENERATED ALWAYS AS (
            CASE WHEN is_default = TRUE THEN user_id ELSE NULL END
        ) STORED,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_addresses_id PRIMARY KEY (id),

    CONSTRAINT nn_addresses_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_addresses_recipient_name CHECK (recipient_name IS NOT NULL),
    CONSTRAINT nn_addresses_phone CHECK (phone IS NOT NULL),
    CONSTRAINT nn_addresses_street CHECK (street IS NOT NULL),
    CONSTRAINT nn_addresses_city CHECK (city IS NOT NULL),
    CONSTRAINT nn_addresses_postal_code CHECK (postal_code IS NOT NULL),
    CONSTRAINT nn_addresses_province CHECK (province IS NOT NULL),
    CONSTRAINT nn_addresses_country CHECK (country IS NOT NULL),

    CONSTRAINT fk_addresses_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uk_addresses_one_default UNIQUE (default_user_id)
) ENGINE=InnoDB;

-- =============
-- 3. CATEGORIAS
-- =============
CREATE TABLE categories (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    name VARCHAR(100),
    description TEXT,
    image_url VARCHAR(500),
    parent_id BIGINT UNSIGNED,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_categories_id PRIMARY KEY (id),

    CONSTRAINT nn_categories_name CHECK (name IS NOT NULL),
    CONSTRAINT nn_categories_is_active CHECK (is_active IS NOT NULL),

    CONSTRAINT fk_categories_parent_id
        FOREIGN KEY (parent_id)
        REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uk_categories_name UNIQUE (name)
) ENGINE=InnoDB;


-- ==========
-- 4. CUPONES
-- ==========
CREATE TABLE coupons (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    code VARCHAR(50),
    description VARCHAR(255),
    discount_type ENUM('PERCENTAGE', 'FIXED'),
    discount_value DECIMAL(10,2),
    min_purchase DECIMAL(10,2) DEFAULT 0.00,
    max_uses INT UNSIGNED,
    used_count INT UNSIGNED DEFAULT 0,
    start_date DATETIME,
    end_date DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_coupons_id PRIMARY KEY (id),

    CONSTRAINT nn_coupons_code CHECK (code IS NOT NULL),
    CONSTRAINT nn_coupons_discount_type CHECK (discount_type IS NOT NULL),
    CONSTRAINT nn_coupons_discount_value CHECK (discount_value IS NOT NULL),
    CONSTRAINT nn_coupons_min_purchase CHECK (min_purchase IS NOT NULL),
    CONSTRAINT nn_coupons_used_count CHECK (used_count IS NOT NULL),
    CONSTRAINT nn_coupons_is_active CHECK (is_active IS NOT NULL),

    CONSTRAINT uk_coupons_code UNIQUE (code),

    CONSTRAINT chk_coupons_discount_value CHECK (discount_value > 0),
    CONSTRAINT chk_coupons_min_purchase CHECK (min_purchase >= 0),
    CONSTRAINT chk_coupons_percentage CHECK (
        discount_type <> 'PERCENTAGE' OR discount_value <= 100
    ),
    CONSTRAINT chk_coupons_usage CHECK (
        max_uses IS NULL OR used_count <= max_uses
    ),
    CONSTRAINT chk_coupons_dates CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date < end_date
    )
) ENGINE=InnoDB;


-- ============
-- 5. PRODUCTOS
-- ============
CREATE TABLE products (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    category_id BIGINT UNSIGNED,
    name VARCHAR(180),
    sku VARCHAR(80),
    description TEXT,
    price DECIMAL(10,2),
    stock INT UNSIGNED DEFAULT 0,
    status ENUM('ACTIVE', 'INACTIVE', 'OUT_OF_STOCK') DEFAULT 'ACTIVE',
    is_featured BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_products_id PRIMARY KEY (id),

    CONSTRAINT nn_products_category_id CHECK (category_id IS NOT NULL),
    CONSTRAINT nn_products_name CHECK (name IS NOT NULL),
    CONSTRAINT nn_products_sku CHECK (sku IS NOT NULL),
    CONSTRAINT nn_products_price CHECK (price IS NOT NULL),
    CONSTRAINT nn_products_stock CHECK (stock IS NOT NULL),
    CONSTRAINT nn_products_status CHECK (status IS NOT NULL),

    CONSTRAINT fk_products_category_id
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uk_products_sku UNIQUE (sku),

    CONSTRAINT chk_products_price CHECK (price >= 0),
    CONSTRAINT chk_products_status CHECK (
        status IN ('ACTIVE', 'INACTIVE', 'OUT_OF_STOCK')
    )
) ENGINE=InnoDB;

-- ===================
-- 6. PRODUCTOS IMAGEN
-- ===================

CREATE TABLE product_images (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    product_id BIGINT UNSIGNED,
    image_url VARCHAR(500),
    is_main BOOLEAN DEFAULT FALSE,

    main_product_id BIGINT UNSIGNED
        GENERATED ALWAYS AS (
            CASE WHEN is_main = TRUE THEN product_id ELSE NULL END
        ) STORED,

    position INT UNSIGNED DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_product_images_id PRIMARY KEY (id),

    CONSTRAINT nn_product_images_product_id CHECK (product_id IS NOT NULL),
    CONSTRAINT nn_product_images_image_url CHECK (image_url IS NOT NULL),
    CONSTRAINT nn_product_images_is_main CHECK (is_main IS NOT NULL),
    CONSTRAINT nn_product_images_position CHECK (position IS NOT NULL),

    CONSTRAINT fk_product_images_product_id
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uk_product_images_main UNIQUE (main_product_id)
) ENGINE=InnoDB;

-- ==========
-- 7. CARRITO
-- ==========
CREATE TABLE carts (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    user_id BIGINT UNSIGNED,
    status ENUM('ACTIVE', 'CONVERTED', 'ABANDONED') DEFAULT 'ACTIVE',

    active_user_id BIGINT UNSIGNED
        GENERATED ALWAYS AS (
            CASE WHEN status = 'ACTIVE' THEN user_id ELSE NULL END
        ) STORED,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_carts_id PRIMARY KEY (id),

    CONSTRAINT nn_carts_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_carts_status CHECK (status IS NOT NULL),

    CONSTRAINT fk_carts_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uk_carts_active_user UNIQUE (active_user_id),

    CONSTRAINT chk_carts_status CHECK (
        status IN ('ACTIVE', 'CONVERTED', 'ABANDONED')
    )
) ENGINE=InnoDB;

-- ====================
-- 8. CARRITO PRODUCTOS
-- ====================
CREATE TABLE cart_items (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    cart_id BIGINT UNSIGNED,
    product_id BIGINT UNSIGNED,
    quantity INT UNSIGNED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_cart_items_id PRIMARY KEY (id),

    CONSTRAINT nn_cart_items_cart_id CHECK (cart_id IS NOT NULL),
    CONSTRAINT nn_cart_items_product_id CHECK (product_id IS NOT NULL),
    CONSTRAINT nn_cart_items_quantity CHECK (quantity IS NOT NULL),

    CONSTRAINT fk_cart_items_cart_id
        FOREIGN KEY (cart_id)
        REFERENCES carts(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_cart_items_product_id
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uk_cart_items_cart_product UNIQUE (cart_id, product_id),

    CONSTRAINT chk_cart_items_quantity CHECK (quantity > 0)
) ENGINE=InnoDB;

-- ============
-- 9. FAVORITOS
-- ============
CREATE TABLE favorites (
    user_id BIGINT UNSIGNED,
    product_id BIGINT UNSIGNED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_favorites_user_product PRIMARY KEY (user_id, product_id),

    CONSTRAINT nn_favorites_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_favorites_product_id CHECK (product_id IS NOT NULL),

    CONSTRAINT fk_favorites_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_favorites_product_id
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ===========
-- 10. PEDIDOS
-- ===========
CREATE TABLE orders (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    order_number VARCHAR(40),
    user_id BIGINT UNSIGNED,
    coupon_id BIGINT UNSIGNED,

    recipient_name VARCHAR(160),
    phone VARCHAR(25),
    street VARCHAR(220),
    city VARCHAR(100),
    postal_code VARCHAR(15),
    province VARCHAR(100),
    country VARCHAR(100) DEFAULT 'España',

    subtotal DECIMAL(10,2),
    discount DECIMAL(10,2) DEFAULT 0.00,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2),

    status ENUM(
        'PENDING', 'CONFIRMED', 'PREPARING',
        'SHIPPED', 'DELIVERED', 'CANCELLED'
    ) DEFAULT 'PENDING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_orders_id PRIMARY KEY (id),

    CONSTRAINT nn_orders_order_number CHECK (order_number IS NOT NULL),
    CONSTRAINT nn_orders_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_orders_recipient_name CHECK (recipient_name IS NOT NULL),
    CONSTRAINT nn_orders_phone CHECK (phone IS NOT NULL),
    CONSTRAINT nn_orders_street CHECK (street IS NOT NULL),
    CONSTRAINT nn_orders_city CHECK (city IS NOT NULL),
    CONSTRAINT nn_orders_postal_code CHECK (postal_code IS NOT NULL),
    CONSTRAINT nn_orders_province CHECK (province IS NOT NULL),
    CONSTRAINT nn_orders_country CHECK (country IS NOT NULL),
    CONSTRAINT nn_orders_subtotal CHECK (subtotal IS NOT NULL),
    CONSTRAINT nn_orders_discount CHECK (discount IS NOT NULL),
    CONSTRAINT nn_orders_shipping_cost CHECK (shipping_cost IS NOT NULL),
    CONSTRAINT nn_orders_total CHECK (total IS NOT NULL),
    CONSTRAINT nn_orders_status CHECK (status IS NOT NULL),

    CONSTRAINT fk_orders_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_orders_coupon_id
        FOREIGN KEY (coupon_id)
        REFERENCES coupons(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uk_orders_order_number UNIQUE (order_number),

    CONSTRAINT chk_orders_subtotal CHECK (subtotal >= 0),
    CONSTRAINT chk_orders_discount CHECK (discount >= 0 AND discount <= subtotal),
    CONSTRAINT chk_orders_shipping CHECK (shipping_cost >= 0),
    CONSTRAINT chk_orders_total CHECK (
        total = subtotal - discount + shipping_cost
    ),
    CONSTRAINT chk_orders_status CHECK (
        status IN (
            'PENDING', 'CONFIRMED', 'PREPARING',
            'SHIPPED', 'DELIVERED', 'CANCELLED'
        )
    )
) ENGINE=InnoDB;

-- =====================
-- 11. PROCUCTOS PEDIDOS
-- =====================
CREATE TABLE order_items (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    order_id BIGINT UNSIGNED,
    product_id BIGINT UNSIGNED,
    product_name VARCHAR(180),
    product_sku VARCHAR(80),
    unit_price DECIMAL(10,2),
    quantity INT UNSIGNED,
    subtotal DECIMAL(10,2),

    CONSTRAINT pk_order_items_id PRIMARY KEY (id),

    CONSTRAINT nn_order_items_order_id CHECK (order_id IS NOT NULL),
    CONSTRAINT nn_order_items_product_id CHECK (product_id IS NOT NULL),
    CONSTRAINT nn_order_items_product_name CHECK (product_name IS NOT NULL),
    CONSTRAINT nn_order_items_product_sku CHECK (product_sku IS NOT NULL),
    CONSTRAINT nn_order_items_unit_price CHECK (unit_price IS NOT NULL),
    CONSTRAINT nn_order_items_quantity CHECK (quantity IS NOT NULL),
    CONSTRAINT nn_order_items_subtotal CHECK (subtotal IS NOT NULL),

    CONSTRAINT fk_order_items_order_id
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_order_items_product_id
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_order_items_price CHECK (unit_price >= 0),
    CONSTRAINT chk_order_items_quantity CHECK (quantity > 0),
    CONSTRAINT chk_order_items_subtotal CHECK (
        subtotal = unit_price * quantity
    )
) ENGINE=InnoDB;

-- =========
-- 12. PAGOS
-- =========
CREATE TABLE payments (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    order_id BIGINT UNSIGNED,
    payment_method ENUM('CARD', 'PAYPAL', 'SIMULATED') DEFAULT 'SIMULATED',
    amount DECIMAL(10,2),
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'REFUNDED') DEFAULT 'PENDING',
    transaction_reference VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_payments_id PRIMARY KEY (id),

    CONSTRAINT nn_payments_order_id CHECK (order_id IS NOT NULL),
    CONSTRAINT nn_payments_payment_method CHECK (payment_method IS NOT NULL),
    CONSTRAINT nn_payments_amount CHECK (amount IS NOT NULL),
    CONSTRAINT nn_payments_status CHECK (status IS NOT NULL),

    CONSTRAINT fk_payments_order_id
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uk_payments_transaction_reference UNIQUE (transaction_reference),

    CONSTRAINT chk_payments_amount CHECK (amount >= 0),
    CONSTRAINT chk_payments_status CHECK (
        status IN ('PENDING', 'APPROVED', 'REJECTED', 'REFUNDED')
    )
) ENGINE=InnoDB;

-- ==============
-- 13. MOVIMIENTO
-- ==============
CREATE TABLE stock_movements (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    product_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    movement_type ENUM('ENTRY', 'SALE', 'RETURN', 'ADJUSTMENT'),
    quantity INT UNSIGNED,
    previous_stock INT UNSIGNED,
    new_stock INT UNSIGNED,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_stock_movements_id PRIMARY KEY (id),

    CONSTRAINT nn_stock_movements_product_id CHECK (product_id IS NOT NULL),
    CONSTRAINT nn_stock_movements_type CHECK (movement_type IS NOT NULL),
    CONSTRAINT nn_stock_movements_quantity CHECK (quantity IS NOT NULL),
    CONSTRAINT nn_stock_movements_previous_stock CHECK (previous_stock IS NOT NULL),
    CONSTRAINT nn_stock_movements_new_stock CHECK (new_stock IS NOT NULL),

    CONSTRAINT fk_stock_movements_product_id
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_stock_movements_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_stock_movements_quantity CHECK (quantity > 0)
) ENGINE=InnoDB;


-- =================
-- 14. CANJE CUPONES
-- =================
CREATE TABLE coupon_redemptions (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    coupon_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    order_id BIGINT UNSIGNED,
    discount_applied DECIMAL(10,2),
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_coupon_redemptions_id PRIMARY KEY (id),

    CONSTRAINT nn_coupon_redemptions_coupon_id CHECK (coupon_id IS NOT NULL),
    CONSTRAINT nn_coupon_redemptions_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_coupon_redemptions_order_id CHECK (order_id IS NOT NULL),
    CONSTRAINT nn_coupon_redemptions_discount CHECK (discount_applied IS NOT NULL),

    CONSTRAINT fk_coupon_redemptions_coupon_id
        FOREIGN KEY (coupon_id)
        REFERENCES coupons(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_coupon_redemptions_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_coupon_redemptions_order_id
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uk_coupon_redemptions_coupon_user UNIQUE (coupon_id, user_id),
    CONSTRAINT uk_coupon_redemptions_order UNIQUE (order_id),

    CONSTRAINT chk_coupon_redemptions_discount CHECK (discount_applied >= 0)
) ENGINE=InnoDB;

-- ===========
-- 15. EVENTOS
-- ===========
CREATE TABLE events (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    title VARCHAR(180),
    description TEXT,
    event_type ENUM('TOURNAMENT', 'RELEASE', 'CASUAL', 'WORKSHOP', 'SPECIAL')
        DEFAULT 'TOURNAMENT',
    game_name VARCHAR(100),
    image_url VARCHAR(500),
    location VARCHAR(220),
    event_date DATETIME,
    end_date DATETIME,
    max_participants INT UNSIGNED,
    entry_fee DECIMAL(10,2) DEFAULT 0.00,
    prize_description TEXT,
    status ENUM('DRAFT', 'PUBLISHED', 'FULL', 'CANCELLED', 'COMPLETED')
        DEFAULT 'DRAFT',
    created_by BIGINT UNSIGNED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_events_id PRIMARY KEY (id),

    CONSTRAINT nn_events_title CHECK (title IS NOT NULL),
    CONSTRAINT nn_events_event_type CHECK (event_type IS NOT NULL),
    CONSTRAINT nn_events_location CHECK (location IS NOT NULL),
    CONSTRAINT nn_events_event_date CHECK (event_date IS NOT NULL),
    CONSTRAINT nn_events_max_participants CHECK (max_participants IS NOT NULL),
    CONSTRAINT nn_events_entry_fee CHECK (entry_fee IS NOT NULL),
    CONSTRAINT nn_events_status CHECK (status IS NOT NULL),
    CONSTRAINT nn_events_created_by CHECK (created_by IS NOT NULL),

    CONSTRAINT fk_events_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_events_capacity CHECK (max_participants > 0),
    CONSTRAINT chk_events_entry_fee CHECK (entry_fee >= 0),
    CONSTRAINT chk_events_dates CHECK (
        end_date IS NULL OR event_date < end_date
    )
) ENGINE=InnoDB;

-- ====================
-- 16. EVENTOS REGISTRO
-- ====================
CREATE TABLE event_registrations (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    event_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('CONFIRMED', 'WAITLIST', 'CANCELLED', 'ATTENDED', 'NO_SHOW')
        DEFAULT 'CONFIRMED',
    payment_status ENUM('NOT_REQUIRED', 'PENDING', 'PAID', 'REFUNDED')
        DEFAULT 'NOT_REQUIRED',

    CONSTRAINT pk_event_registrations_id PRIMARY KEY (id),

    CONSTRAINT nn_event_registrations_event_id CHECK (event_id IS NOT NULL),
    CONSTRAINT nn_event_registrations_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_event_registrations_status CHECK (status IS NOT NULL),
    CONSTRAINT nn_event_registrations_payment_status CHECK (payment_status IS NOT NULL),

    CONSTRAINT fk_event_registrations_event_id
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_event_registrations_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uk_event_registrations_event_user UNIQUE (event_id, user_id),

    CONSTRAINT chk_event_registrations_status CHECK (
        status IN ('CONFIRMED', 'WAITLIST', 'CANCELLED', 'ATTENDED', 'NO_SHOW')
    ),

    CONSTRAINT chk_event_registrations_payment CHECK (
        payment_status IN ('NOT_REQUIRED', 'PENDING', 'PAID', 'REFUNDED')
    )
) ENGINE=InnoDB;


-- ======================
-- 16. EVENTOS RESULTADOS
-- ======================
CREATE TABLE event_results (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    event_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    position INT UNSIGNED,
    points DECIMAL(8,2) DEFAULT 0.00,
    prize VARCHAR(180),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_event_results_id PRIMARY KEY (id),

    CONSTRAINT nn_event_results_event_id CHECK (event_id IS NOT NULL),
    CONSTRAINT nn_event_results_user_id CHECK (user_id IS NOT NULL),
    CONSTRAINT nn_event_results_position CHECK (position IS NOT NULL),
    CONSTRAINT nn_event_results_points CHECK (points IS NOT NULL),

    CONSTRAINT fk_event_results_registration
        FOREIGN KEY (event_id, user_id)
        REFERENCES event_registrations(event_id, user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uk_event_results_event_user UNIQUE (event_id, user_id),
    CONSTRAINT uk_event_results_event_position UNIQUE (event_id, position),

    CONSTRAINT chk_event_results_position CHECK (position > 0),
    CONSTRAINT chk_event_results_points CHECK (points >= 0)
) ENGINE=InnoDB;