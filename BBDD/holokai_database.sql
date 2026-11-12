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