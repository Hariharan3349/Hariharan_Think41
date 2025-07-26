import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "ecommerce.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database and load CSV data"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.load_csv_data()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def load_csv_data(self):
        """Load CSV files into SQLite database"""
        csv_files = [
            'distribution_centers.csv',
            'products.csv', 
            'users.csv',
            'orders.csv',
            'order_items.csv',
            'inventory_items.csv'
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    table_name = csv_file.replace('.csv', '')
                    df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                    logger.info(f"Loaded {csv_file} into {table_name} table")
                except Exception as e:
                    logger.error(f"Error loading {csv_file}: {e}")
    
    def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products with basic information"""
        query = """
        SELECT id, name, brand, category, department, retail_price, cost
        FROM products 
        LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=[limit])
        return df.to_dict('records')
    
    def search_products(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search products by name, brand, or category"""
        query = """
        SELECT id, name, brand, category, department, retail_price, cost
        FROM products 
        WHERE LOWER(name) LIKE LOWER(?) 
           OR LOWER(brand) LIKE LOWER(?) 
           OR LOWER(category) LIKE LOWER(?)
        LIMIT ?
        """
        search_pattern = f"%{search_term}%"
        df = pd.read_sql_query(query, self.conn, params=[search_pattern, search_pattern, search_pattern, limit])
        return df.to_dict('records')
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get detailed product information by ID"""
        query = """
        SELECT p.*, dc.name as distribution_center_name
        FROM products p
        LEFT JOIN distribution_centers dc ON p.distribution_center_id = dc.id
        WHERE p.id = ?
        """
        df = pd.read_sql_query(query, self.conn, params=[product_id])
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
    
    def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get orders for a specific user"""
        query = """
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
        """
        df = pd.read_sql_query(query, self.conn, params=[user_id])
        return df.to_dict('records')
    
    def get_order_details(self, order_id: int) -> List[Dict[str, Any]]:
        """Get detailed order items for an order"""
        query = """
        SELECT oi.*, p.name as product_name, p.brand, p.category
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
        """
        df = pd.read_sql_query(query, self.conn, params=[order_id])
        return df.to_dict('records')
    
    def get_inventory_status(self, product_id: int) -> Dict[str, Any]:
        """Get inventory status for a product"""
        query = """
        SELECT 
            COUNT(*) as total_items,
            COUNT(CASE WHEN sold_at IS NULL THEN 1 END) as available_items,
            COUNT(CASE WHEN sold_at IS NOT NULL THEN 1 END) as sold_items
        FROM inventory_items
        WHERE product_id = ?
        """
        df = pd.read_sql_query(query, self.conn, params=[product_id])
        if not df.empty:
            return df.iloc[0].to_dict()
        return {"total_items": 0, "available_items": 0, "sold_items": 0}
    
    def get_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular products based on sales"""
        query = """
        SELECT 
            p.id, p.name, p.brand, p.category, p.retail_price,
            COUNT(oi.id) as sales_count
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        GROUP BY p.id
        ORDER BY sales_count DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=[limit])
        return df.to_dict('records')
    
    def get_categories(self) -> List[str]:
        """Get all product categories"""
        query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL"
        df = pd.read_sql_query(query, self.conn)
        return df['category'].tolist()
    
    def get_brands(self) -> List[str]:
        """Get all product brands"""
        query = "SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL"
        df = pd.read_sql_query(query, self.conn)
        return df['brand'].tolist()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Global database instance
db_manager = DatabaseManager() 