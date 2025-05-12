const jwt = require('jsonwebtoken');
const { pool } = require('../models/db');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

const authMiddleware = {
  async verifyToken(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = decoded;
      next();
    } catch (error) {
      return res.status(401).json({ message: 'Invalid token' });
    }
  },

  checkRole(roles) {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ message: 'Unauthorized' });
      }

      const hasRole = req.user.roles.some(role => roles.includes(role));
      
      if (!hasRole) {
        return res.status(403).json({ message: 'Forbidden - Insufficient role' });
      }

      next();
    };
  },

  checkPermission(permissions) {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ message: 'Unauthorized' });
      }

      const hasPermission = permissions.every(permission =>
        req.user.permissions.includes(permission)
      );

      if (!hasPermission) {
        return res.status(403).json({ message: 'Forbidden - Insufficient permissions' });
      }

      next();
    };
  },

  checkTenant(req, res, next) {
    if (!req.user) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    // Add tenantId to query parameters
    req.query.tenantId = req.user.tenantId;
    next();
  }
};

module.exports = authMiddleware;