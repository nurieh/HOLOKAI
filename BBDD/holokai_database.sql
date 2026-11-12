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
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    recipient_name VARCHAR(160) NOT NULL,
    phone VARCHAR(25) NOT NULL,
    street VARCHAR(220) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(15) NOT NULL,
    province VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'España',
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    default_user_id BIGINT UNSIGNED
        GENERATED ALWAYS AS (CASE WHEN is_default = TRUE THEN user_id ELSE NULL END) STORED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_addresses_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_addresses_one_default UNIQUE (default_user_id),
    INDEX idx_addresses_user (user_id)
) ENGINE=InnoDB;