const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../models/db');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = '24h';

const authController = {
  async register(req, res) {
    const { name, email, password, organization } = req.body;

    if (!organization) {
      return res.status(400).json({ message: 'Organization name is required' });
    }

    try {
      // Start a transaction
      const client = await pool.connect();
      
      try {
        await client.query('BEGIN');

        // Check if user exists
        const userExists = await client.query(
          'SELECT * FROM users WHERE email = $1',
          [email]
        );

        if (userExists.rows.length > 0) {
          throw new Error('User already exists');
        }

        // Create tenant for the organization
        const tenantResult = await client.query(
          'INSERT INTO tenants (name) VALUES ($1) RETURNING id',
          [organization]
        );
        
        const tenantId = tenantResult.rows[0].id;

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Create user
        const userResult = await client.query(
          'INSERT INTO users (name, email, password_hash, tenant_id) VALUES ($1, $2, $3, $4) RETURNING id',
          [name, email, hashedPassword, tenantId]
        );

        // Assign default role (USER) and ADMIN role since this is the first user of the organization
        await client.query(
          `INSERT INTO user_roles (user_id, role_id) 
           SELECT $1, id FROM roles 
           WHERE name IN ('USER', 'ADMIN')`,
          [userResult.rows[0].id]
        );

        await client.query('COMMIT');

        res.status(201).json({ 
          message: 'Registration successful',
          organization: {
            name: organization,
            tenantId: tenantId
          }
        });

      } catch (error) {
        await client.query('ROLLBACK');
        throw error;
      } finally {
        client.release();
      }

    } catch (error) {
      console.error('Registration error:', error);
      res.status(400).json({ message: error.message || 'Registration failed' });
    }
  },

  async login(req, res) {
    const { email, password } = req.body;

    try {
      // Get user with roles and tenant info
      const result = await pool.query(`
        SELECT u.*, array_agg(r.name) as roles, t.name as organization
        FROM users u 
        LEFT JOIN user_roles ur ON u.id = ur.user_id 
        LEFT JOIN roles r ON ur.role_id = r.id 
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.email = $1 
        GROUP BY u.id, t.name`,
        [email]
      );

      const user = result.rows[0];

      if (!user) {
        return res.status(401).json({ message: 'Invalid credentials' });
      }

      const isMatch = await bcrypt.compare(password, user.password_hash);

      if (!isMatch) {
        return res.status(401).json({ message: 'Invalid credentials' });
      }

      // Get user permissions
      const permissionsResult = await pool.query(`
        SELECT DISTINCT p.name 
        FROM permissions p 
        JOIN role_permissions rp ON p.id = rp.permission_id 
        JOIN user_roles ur ON rp.role_id = ur.role_id 
        WHERE ur.user_id = $1`,
        [user.id]
      );

      const permissions = permissionsResult.rows.map(p => p.name);

      // Create token
      const token = jwt.sign(
        {
          id: user.id,
          email: user.email,
          name: user.name,
          tenantId: user.tenant_id,
          organization: user.organization,
          roles: user.roles,
          permissions
        },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      res.json({ token });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ message: 'Server error' });
    }
  },

  async refreshToken(req, res) {
    try {
      const user = req.user; // Set by auth middleware
      const token = jwt.sign(
        {
          id: user.id,
          email: user.email,
          name: user.name,
          tenantId: user.tenant_id,
          organization: user.organization,
          roles: user.roles,
          permissions: user.permissions
        },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      res.json({ token });
    } catch (error) {
      console.error('Token refresh error:', error);
      res.status(500).json({ message: 'Server error' });
    }
  }
};

module.exports = authController;