module.exports = {
  contextToAppId: ({ securityContext }) => {
    return `APP_${securityContext.user_id || 'anonymous'}`;
  },
  
  contextToOrchestratorId: ({ securityContext }) => {
    return `ORCH_${securityContext.user_id || 'default'}`;
  },

  // Security context from JWT token
  checkAuth: async (req, auth) => {
    // For development, allow all requests
    // In production, implement proper JWT validation
    return {
      user_id: req.headers['x-user-id'] || 'anonymous',
      roles: ['user']
    };
  },

  // Repository configuration
  repositoryFactory: ({ securityContext }) => {
    return {
      dataSchemaFiles: () => Promise.resolve([
        {
          fileName: 'Sales.js',
          content: `
cube('Sales', {
  sql: 'SELECT * FROM sales_data',
  
  dimensions: {
    id: {
      sql: 'id',
      type: 'number',
      primaryKey: true
    },
    
    saleDate: {
      sql: 'sale_date',
      type: 'time'
    },
    
    productName: {
      sql: 'product_name',
      type: 'string'
    },
    
    category: {
      sql: 'category',
      type: 'string'
    },
    
    region: {
      sql: 'region',
      type: 'string'
    },
    
    salesRep: {
      sql: 'sales_rep',
      type: 'string'
    },
    
    customerId: {
      sql: 'customer_id',
      type: 'number'
    }
  },
  
  measures: {
    count: {
      type: 'count'
    },
    
    totalAmount: {
      sql: 'total_amount',
      type: 'sum',
      format: 'currency'
    },
    
    averageAmount: {
      sql: 'total_amount',
      type: 'avg',
      format: 'currency'
    },
    
    totalQuantity: {
      sql: 'quantity',
      type: 'sum'
    },
    
    averageQuantity: {
      sql: 'quantity',
      type: 'avg'
    },
    
    uniqueCustomers: {
      sql: 'customer_id',
      type: 'countDistinct'
    }
  },
  
  preAggregations: {
    main: {
      type: 'rollup',
      measureReferences: [Sales.totalAmount, Sales.count],
      dimensionReferences: [Sales.saleDate, Sales.region, Sales.category],
      timeDimensionReference: Sales.saleDate,
      granularity: 'day'
    },
    
    monthly: {
      type: 'rollup',
      measureReferences: [Sales.totalAmount, Sales.count],
      dimensionReferences: [Sales.region, Sales.category],
      timeDimensionReference: Sales.saleDate,
      granularity: 'month'
    }
  }
});
          `
        },
        {
          fileName: 'Customers.js',
          content: `
cube('Customers', {
  sql: 'SELECT * FROM customers',
  
  dimensions: {
    id: {
      sql: 'id',
      type: 'number',
      primaryKey: true
    },
    
    customerName: {
      sql: 'customer_name',
      type: 'string'
    },
    
    email: {
      sql: 'email',
      type: 'string'
    },
    
    company: {
      sql: 'company',
      type: 'string'
    },
    
    industry: {
      sql: 'industry',
      type: 'string'
    },
    
    region: {
      sql: 'region',
      type: 'string'
    },
    
    createdAt: {
      sql: 'created_at',
      type: 'time'
    }
  },
  
  measures: {
    count: {
      type: 'count'
    }
  },
  
  joins: {
    Sales: {
      relationship: 'hasMany',
      sql: \`\${CUBE}.id = \${Sales}.customer_id\`
    }
  }
});
          `
        },
        {
          fileName: 'Products.js',
          content: `
cube('Products', {
  sql: 'SELECT * FROM products',
  
  dimensions: {
    id: {
      sql: 'id',
      type: 'number',
      primaryKey: true
    },
    
    productName: {
      sql: 'product_name',
      type: 'string'
    },
    
    category: {
      sql: 'category',
      type: 'string'
    },
    
    supplier: {
      sql: 'supplier',
      type: 'string'
    },
    
    createdAt: {
      sql: 'created_at',
      type: 'time'
    }
  },
  
  measures: {
    count: {
      type: 'count'
    },
    
    averagePrice: {
      sql: 'price',
      type: 'avg',
      format: 'currency'
    },
    
    averageCost: {
      sql: 'cost',
      type: 'avg',
      format: 'currency'
    }
  }
});
          `
        }
      ])
    };
  },

  // Database configuration
  driverFactory: () => {
    return {};
  },

  // Development mode settings
  devServer: {
    port: 4000
  },

  // API configuration
  http: {
    cors: {
      origin: true,
      credentials: true
    }
  },

  // Query caching
  cacheAndQueueDriver: 'memory',

  // Telemetry
  telemetry: false
};