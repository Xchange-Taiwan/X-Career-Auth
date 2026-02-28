-- ----------------------------
-- Table structure for mail_template
-- ----------------------------
CREATE TABLE mail_template (
  id VARCHAR(20) PRIMARY KEY,
  name TEXT,
  title VARCHAR(200),
  content TEXT,
  -- use TEXT instead of MEDIUMTEXT in PostgreSQL
  description TEXT,
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO mail_template (
    id,
    content,
    name,
    title,
    description,
    create_time,
    update_time
) VALUES (
    'auth_template',
    $$<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; line-height: 1.6; }
        .container { max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        .button { display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px; }
        .verification-code { font-size: 24px; color: #007bff; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        {% if template_type == 'verification_code' %}
            <h2>{{ title }}</h2>
            <p>You are performing an important operation. Please enter the following verification code in the form to complete the process:</p>
            <p class="verification-code">{{ confirm_code }}</p>
            <p>Please note that this verification code will expire in 5 minutes.</p>
        {% elif template_type == 'signup' %}
            <h2>Welcome to {{ site_title }}!</h2>
            <p>Thank you for registering with us! Please confirm your email to complete your registration.</p>
            <a href="{{ confirm_url }}" class="button">Confirm Your Email</a>
            <p>If you did not register for an account, please ignore this email or contact support if you have questions.</p>
            <p>Welcome aboard!</p>
        {% elif template_type == 'reset_password' %}
            <h2>Password Reset Request</h2>
            <p>Click the button below to reset your password:</p>
            <a href="{{ reset_url }}" class="button">Reset Your Password</a>
            <p>If you did not request a password reset, please ignore this email or contact support if you have questions.</p>
            <p> Thank you !</p>
        {% endif %}
    </div>
</body>
</html>$$,
    'Auth Email Template',
    'Auth Email',
    'A template that can be used for verification, signup, or reset emails.',
    NOW(),
    NOW()
);
