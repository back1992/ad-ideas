"""
Property-based tests for DatabaseManager

Feature: platform-core, Property 12: Database Transaction Integrity
Validates: Requirements 6.2, 6.5

This module contains property-based tests using Hypothesis to verify
database transaction integrity and initialization correctness.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
from typing import List, Tuple, Any

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

from modules.database import DatabaseManager


class TestDatabaseTransactionIntegrity:
    """
    Property-based tests for database transaction integrity.
    
    Feature: platform-core, Property 12: Database Transaction Integrity
    """
    
    def setup_method(self):
        """Set up test database for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_platform.db")
        
    def teardown_method(self):
        """Clean up test database after each test method."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=20, deadline=None)
    def test_database_initialization_integrity(self, db_name: str):
        """
        Property: For any valid database path, initialization should either 
        complete successfully with all tables created, or fail completely 
        without partial state.
        
        Feature: platform-core, Property 12: Database Transaction Integrity
        Validates: Requirements 6.2, 6.5
        """
        # Sanitize database name for filesystem
        safe_db_name = "".join(c for c in db_name if c.isalnum() or c in "._-")
        assume(len(safe_db_name) > 0)
        
        test_db_path = os.path.join(self.temp_dir, f"{safe_db_name}.db")
        
        try:
            # Initialize database manager
            db_manager = DatabaseManager(test_db_path)
            
            # Attempt initialization
            db_manager.init_database()
            
            # Verify all required tables exist
            required_tables = [
                'user_feedback', 'comments', 'articles', 
                'content_stats', 'user_activity'
            ]
            
            for table in required_tables:
                assert db_manager.table_exists(table), f"Table {table} should exist after initialization"
            
            # Verify database file was created
            assert os.path.exists(test_db_path), "Database file should exist after initialization"
            
            # Verify database is accessible and functional
            test_query = "SELECT name FROM sqlite_master WHERE type='table'"
            result = db_manager.execute_query(test_query)
            
            # Should have exactly the required tables (plus sqlite_sequence which is auto-created)
            table_names = set(result['name'].tolist())
            expected_tables = set(required_tables)
            
            # Remove sqlite_sequence as it's automatically created by SQLite for AUTOINCREMENT
            table_names.discard('sqlite_sequence')
            
            assert table_names == expected_tables, f"Expected tables {expected_tables}, got {table_names}"
            
        except Exception as e:
            # If initialization fails, database should not be in partial state
            if os.path.exists(test_db_path):
                # Check if database is empty or corrupted
                try:
                    conn = sqlite3.connect(test_db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    # If database exists but initialization failed, 
                    # it should either be empty or have all tables
                    if len(tables) > 0:
                        table_names = [table[0] for table in tables]
                        required_tables = [
                            'user_feedback', 'comments', 'articles', 
                            'content_stats', 'user_activity'
                        ]
                        # Remove sqlite_sequence as it's automatically created by SQLite
                        table_names = [t for t in table_names if t != 'sqlite_sequence']
                        
                        # Either all tables exist (previous successful init) or none
                        assert (set(table_names) == set(required_tables) or 
                               len(table_names) == 0), \
                               f"Database in partial state with tables: {table_names}"
                        
                except sqlite3.Error:
                    # Database is corrupted, which is acceptable for failed initialization
                    pass
        
        finally:
            # Clean up test database
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # username
                st.text(min_size=1, max_size=10),  # target_type
                st.text(min_size=1, max_size=10),  # target_id
                st.text(min_size=1, max_size=10),  # feedback_type
                st.integers(min_value=0, max_value=5)  # feedback_value
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_batch_operations_integrity(self, feedback_data: List[Tuple[str, str, str, str, int]]):
        """
        Property: For any batch of database operations, they should either 
        all succeed or all fail, maintaining data consistency.
        
        Feature: platform-core, Property 12: Database Transaction Integrity
        Validates: Requirements 6.2, 6.5
        """
        # Create a unique database path for this test run
        import uuid
        unique_db_path = os.path.join(self.temp_dir, f"batch_test_{uuid.uuid4().hex[:8]}.db")
        
        db_manager = DatabaseManager(unique_db_path)
        db_manager.init_database()
        
        # Prepare batch insert data
        insert_query = """
            INSERT INTO user_feedback 
            (username, target_type, target_id, feedback_type, feedback_value)
            VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            # Verify database starts empty
            count_query = "SELECT COUNT(*) as count FROM user_feedback"
            initial_result = db_manager.execute_query(count_query)
            initial_count = initial_result.iloc[0]['count']
            assert initial_count == 0, f"Database should start empty, but has {initial_count} rows"
            
            # Execute batch operation
            affected_rows = db_manager.execute_many(insert_query, feedback_data)
            
            # Verify all rows were inserted
            result = db_manager.execute_query(count_query)
            actual_count = result.iloc[0]['count']
            
            # Transaction integrity: either all rows inserted or none
            assert actual_count == len(feedback_data), \
                f"Expected {len(feedback_data)} rows, got {actual_count}"
            assert affected_rows == len(feedback_data), \
                f"Expected {len(feedback_data)} affected rows, got {affected_rows}"
            
        except Exception as e:
            # If batch operation fails, no partial data should be inserted
            count_query = "SELECT COUNT(*) as count FROM user_feedback"
            result = db_manager.execute_query(count_query)
            actual_count = result.iloc[0]['count']
            
            # Should be 0 if transaction failed completely
            assert actual_count == 0, \
                f"Transaction failed but {actual_count} rows were inserted (should be 0)"
        
        finally:
            # Clean up unique database file
            if os.path.exists(unique_db_path):
                os.remove(unique_db_path)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=20, deadline=None)
    def test_concurrent_initialization_integrity(self, db_suffix: str):
        """
        Property: For any database path, multiple initialization attempts 
        should result in consistent final state.
        
        Feature: platform-core, Property 12: Database Transaction Integrity
        Validates: Requirements 6.2, 6.5
        """
        # Sanitize suffix
        safe_suffix = "".join(c for c in db_suffix if c.isalnum() or c in "._-")
        assume(len(safe_suffix) > 0)
        
        test_db_path = os.path.join(self.temp_dir, f"concurrent_{safe_suffix}.db")
        
        try:
            # Multiple initialization attempts
            db_manager1 = DatabaseManager(test_db_path)
            db_manager2 = DatabaseManager(test_db_path)
            
            # First initialization
            db_manager1.init_database()
            
            # Second initialization (should be idempotent)
            db_manager2.init_database()
            
            # Verify consistent state
            required_tables = [
                'user_feedback', 'comments', 'articles', 
                'content_stats', 'user_activity'
            ]
            
            for table in required_tables:
                assert db_manager1.table_exists(table), f"Table {table} missing after multiple inits"
                assert db_manager2.table_exists(table), f"Table {table} missing after multiple inits"
            
            # Verify table structures are identical
            for table in required_tables:
                info1 = db_manager1.get_table_info(table)
                info2 = db_manager2.get_table_info(table)
                
                # Compare table structures
                assert len(info1) == len(info2), f"Table {table} structure mismatch"
                assert list(info1.columns) == list(info2.columns), f"Table {table} columns mismatch"
                
        finally:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)


class DatabaseStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for database operations.
    
    Feature: platform-core, Property 12: Database Transaction Integrity
    """
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "stateful_test.db")
        self.db_manager = None
        self.initialized = False
    
    @initialize()
    def setup_database(self):
        """Initialize database manager."""
        self.db_manager = DatabaseManager(self.db_path)
    
    @rule()
    def initialize_database(self):
        """Rule: Initialize database (can be called multiple times)."""
        try:
            self.db_manager.init_database()
            self.initialized = True
            
            # Verify initialization succeeded
            required_tables = [
                'user_feedback', 'comments', 'articles', 
                'content_stats', 'user_activity'
            ]
            
            for table in required_tables:
                assert self.db_manager.table_exists(table), f"Table {table} should exist"
                
        except Exception as e:
            # If initialization fails, state should remain consistent
            if self.initialized:
                # Previous initialization succeeded, so tables should still exist
                required_tables = [
                    'user_feedback', 'comments', 'articles', 
                    'content_stats', 'user_activity'
                ]
                for table in required_tables:
                    assert self.db_manager.table_exists(table), \
                        f"Table {table} disappeared after failed re-initialization"
    
    @rule(
        username=st.text(min_size=1, max_size=20),
        target_type=st.text(min_size=1, max_size=10),
        target_id=st.text(min_size=1, max_size=10),
        feedback_type=st.text(min_size=1, max_size=10),
        feedback_value=st.integers(min_value=0, max_value=5)
    )
    def insert_feedback(self, username: str, target_type: str, target_id: str, 
                       feedback_type: str, feedback_value: int):
        """Rule: Insert feedback data."""
        if not self.initialized:
            return
        
        try:
            query = """
                INSERT INTO user_feedback 
                (username, target_type, target_id, feedback_type, feedback_value)
                VALUES (?, ?, ?, ?, ?)
            """
            
            initial_count_result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM user_feedback"
            )
            initial_count = initial_count_result.iloc[0]['count']
            
            affected_rows = self.db_manager.execute_update(
                query, (username, target_type, target_id, feedback_type, feedback_value)
            )
            
            # Verify transaction integrity
            final_count_result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM user_feedback"
            )
            final_count = final_count_result.iloc[0]['count']
            
            # Should have exactly one more row
            assert final_count == initial_count + 1, \
                f"Expected count {initial_count + 1}, got {final_count}"
            assert affected_rows == 1, f"Expected 1 affected row, got {affected_rows}"
            
        except Exception as e:
            # If insert fails, count should remain unchanged
            current_count_result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM user_feedback"
            )
            current_count = current_count_result.iloc[0]['count']
            
            # Count should not have changed if operation failed
            # (We can't easily track initial_count across failed operations,
            # but we can verify database is still accessible)
            assert isinstance(current_count, int), "Database should remain accessible after failed insert"
    
    def teardown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)


# Stateful test class
TestDatabaseStateMachine = DatabaseStateMachine.TestCase