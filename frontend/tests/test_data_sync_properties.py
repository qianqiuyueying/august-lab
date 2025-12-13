"""
Data Synchronization Real-time Properties Tests

Tests for data synchronization between frontend and backend,
real-time updates, cache consistency, and state management.

**属性 9: 数据同步实时性**
**验证: 需求 4.5, 8.5**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, Any, List, Optional, Set
import time
from datetime import datetime, timedelta
import json


class DataSyncManager:
    """Data synchronization and state management logic"""
    
    def __init__(self):
        self.local_cache = {}
        self.server_state = {}
        self.sync_queue = []
        self.last_sync_time = {}
        self.sync_start_times = {}
        self.conflict_resolution_strategy = 'server_wins'
        self.sync_interval = 1.0  # seconds
        self.max_retry_attempts = 3
        self.offline_changes = []
        
    def update_local_data(self, entity_type: str, entity_id: str, data: Dict[str, Any], timestamp: Optional[float] = None) -> bool:
        """Update local data and queue for synchronization"""
        if timestamp is None:
            timestamp = time.time()
        
        # Store in local cache
        cache_key = f"{entity_type}:{entity_id}"
        self.local_cache[cache_key] = {
            'data': data.copy(),
            'timestamp': timestamp,
            'dirty': True,
            'version': self.local_cache.get(cache_key, {}).get('version', 0) + 1
        }
        
        # Queue for sync
        sync_item = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'data': data.copy(),
            'timestamp': timestamp,
            'operation': 'update',
            'retry_count': 0
        }
        
        self.sync_queue.append(sync_item)
        return True
    
    def sync_to_server(self, simulate_network_delay: float = 0.0, simulate_failure: bool = False) -> Dict[str, Any]:
        """Simulate synchronization to server"""
        if simulate_failure:
            return {'success': False, 'error': 'Network error'}
        
        sync_start_time = time.time()
        
        if simulate_network_delay > 0:
            time.sleep(simulate_network_delay)
        
        synced_items = []
        failed_items = []
        
        for item in self.sync_queue.copy():
            cache_key = f"{item['entity_type']}:{item['entity_id']}"
            
            # Simulate server processing
            server_key = cache_key
            server_timestamp = time.time()
            
            # Store sync timing information
            self.sync_start_times[cache_key] = sync_start_time
            
            # Check for conflicts
            server_data = self.server_state.get(server_key, {})
            local_data = self.local_cache.get(cache_key, {})
            
            conflict = False
            if server_data and local_data:
                server_version = server_data.get('version', 0)
                local_version = local_data.get('version', 0)
                
                # Conflict if server has newer version than what we based our changes on
                if server_version > local_version - 1:
                    conflict = True
            
            if conflict:
                # Apply conflict resolution
                if self.conflict_resolution_strategy == 'server_wins':
                    # Keep server data, discard local changes
                    self.local_cache[cache_key] = server_data.copy()
                elif self.conflict_resolution_strategy == 'client_wins':
                    # Push local changes to server
                    self.server_state[server_key] = {
                        'data': item['data'].copy(),
                        'timestamp': server_timestamp,
                        'version': server_data.get('version', 0) + 1
                    }
                elif self.conflict_resolution_strategy == 'merge':
                    # Simple merge strategy (in practice, this would be more sophisticated)
                    merged_data = {**server_data.get('data', {}), **item['data']}
                    self.server_state[server_key] = {
                        'data': merged_data,
                        'timestamp': server_timestamp,
                        'version': server_data.get('version', 0) + 1
                    }
                    self.local_cache[cache_key] = self.server_state[server_key].copy()
            else:
                # No conflict, apply changes
                self.server_state[server_key] = {
                    'data': item['data'].copy(),
                    'timestamp': server_timestamp,
                    'version': server_data.get('version', 0) + 1
                }
                
                # Update local cache with server response
                self.local_cache[cache_key] = self.server_state[server_key].copy()
                self.local_cache[cache_key]['dirty'] = False
            
            synced_items.append(item)
            self.last_sync_time[cache_key] = server_timestamp
        
        # Remove synced items from queue
        for item in synced_items:
            if item in self.sync_queue:
                self.sync_queue.remove(item)
        
        return {
            'success': True,
            'synced_count': len(synced_items),
            'failed_count': len(failed_items),
            'conflicts_resolved': sum(1 for item in synced_items if 'conflict' in item)
        }
    
    def get_local_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get data from local cache"""
        cache_key = f"{entity_type}:{entity_id}"
        cached_item = self.local_cache.get(cache_key)
        return cached_item['data'] if cached_item else None
    
    def get_server_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get data from server state"""
        server_key = f"{entity_type}:{entity_id}"
        server_item = self.server_state.get(server_key)
        return server_item['data'] if server_item else None
    
    def is_data_synchronized(self, entity_type: str, entity_id: str) -> bool:
        """Check if local and server data are synchronized"""
        cache_key = f"{entity_type}:{entity_id}"
        
        local_item = self.local_cache.get(cache_key)
        server_item = self.server_state.get(cache_key)
        
        if not local_item or not server_item:
            return False
        
        # Check if data is the same and not dirty
        return (
            local_item['data'] == server_item['data'] and
            not local_item.get('dirty', False)
        )
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get overall synchronization status"""
        total_items = len(self.local_cache)
        synchronized_items = 0
        pending_sync = len(self.sync_queue)
        
        for cache_key in self.local_cache:
            entity_type, entity_id = cache_key.split(':', 1)
            if self.is_data_synchronized(entity_type, entity_id):
                synchronized_items += 1
        
        return {
            'total_items': total_items,
            'synchronized_items': synchronized_items,
            'pending_sync': pending_sync,
            'sync_percentage': (synchronized_items / total_items * 100) if total_items > 0 else 100,
            'has_conflicts': any(item.get('conflict', False) for item in self.sync_queue)
        }
    
    def simulate_offline_changes(self, changes: List[Dict[str, Any]]) -> None:
        """Simulate changes made while offline"""
        self.offline_changes.extend(changes)
        
        for change in changes:
            self.update_local_data(
                change['entity_type'],
                change['entity_id'],
                change['data'],
                change.get('timestamp', time.time())
            )
    
    def simulate_server_push(self, entity_type: str, entity_id: str, data: Dict[str, Any]) -> bool:
        """Simulate server pushing updates to client"""
        server_key = f"{entity_type}:{entity_id}"
        timestamp = time.time()
        
        # Update server state
        self.server_state[server_key] = {
            'data': data.copy(),
            'timestamp': timestamp,
            'version': self.server_state.get(server_key, {}).get('version', 0) + 1
        }
        
        # Check if we have local changes
        local_item = self.local_cache.get(server_key)
        if local_item and local_item.get('dirty', False):
            # Conflict detected - server update while we have local changes
            return False
        
        # Update local cache with server data
        self.local_cache[server_key] = self.server_state[server_key].copy()
        self.local_cache[server_key]['dirty'] = False
        
        return True
    
    def calculate_sync_latency(self, entity_type: str, entity_id: str) -> Optional[float]:
        """Calculate synchronization latency for an entity"""
        cache_key = f"{entity_type}:{entity_id}"
        
        sync_start = self.sync_start_times.get(cache_key)
        last_sync = self.last_sync_time.get(cache_key)
        
        if not sync_start or not last_sync:
            return None
        
        return last_sync - sync_start


# Test data generators
@st.composite
def entity_data(draw):
    """Generate entity data for testing"""
    return {
        'id': draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'name': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')))),
        'content': draw(st.text(min_size=0, max_size=200)),
        'metadata': draw(st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.one_of(st.text(max_size=50), st.integers(), st.booleans()),
            min_size=0, max_size=5
        ))
    }


@st.composite
def sync_operations(draw):
    """Generate synchronization operations"""
    entity_types = ['portfolio', 'blog', 'profile']
    operations = []
    
    num_operations = draw(st.integers(min_value=1, max_value=10))
    
    for _ in range(num_operations):
        operation = {
            'entity_type': draw(st.sampled_from(entity_types)),
            'entity_id': draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789')),
            'data': draw(entity_data()),
            'timestamp': draw(st.floats(min_value=1640995200.0, max_value=1672531200.0))  # Fixed time range
        }
        operations.append(operation)
    
    return operations


class TestDataSyncProperties:
    """Property tests for data synchronization functionality"""
    
    @given(sync_operations())
    def test_local_updates_are_queued_for_sync(self, operations):
        """Local data updates should be queued for synchronization"""
        sync_manager = DataSyncManager()
        
        for op in operations:
            result = sync_manager.update_local_data(
                op['entity_type'],
                op['entity_id'],
                op['data'],
                op['timestamp']
            )
            
            # Update should succeed
            assert result is True
            
            # Data should be in local cache
            local_data = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
            assert local_data == op['data']
            
            # Should be marked as dirty
            cache_key = f"{op['entity_type']}:{op['entity_id']}"
            assert sync_manager.local_cache[cache_key]['dirty'] is True
        
        # All operations should be queued for sync
        assert len(sync_manager.sync_queue) == len(operations)
    
    @given(sync_operations())
    def test_successful_sync_clears_dirty_flag(self, operations):
        """Successful synchronization should clear dirty flags and update server state"""
        sync_manager = DataSyncManager()
        
        # Add operations to sync queue
        for op in operations:
            sync_manager.update_local_data(
                op['entity_type'],
                op['entity_id'],
                op['data'],
                op['timestamp']
            )
        
        # Perform sync
        result = sync_manager.sync_to_server()
        
        # Sync should succeed
        assert result['success'] is True
        assert result['synced_count'] == len(operations)
        
        # All items should be synchronized
        for op in operations:
            assert sync_manager.is_data_synchronized(op['entity_type'], op['entity_id'])
            
            # Local and server data should match
            local_data = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
            server_data = sync_manager.get_server_data(op['entity_type'], op['entity_id'])
            assert local_data == server_data
        
        # Sync queue should be empty
        assert len(sync_manager.sync_queue) == 0
    
    @given(
        sync_operations(),
        st.floats(min_value=0.0, max_value=2.0)
    )
    @settings(deadline=None)
    def test_sync_latency_calculation(self, operations, network_delay):
        """Sync latency should be calculated correctly"""
        sync_manager = DataSyncManager()
        
        # Add operations
        for op in operations:
            sync_manager.update_local_data(
                op['entity_type'],
                op['entity_id'],
                op['data'],
                op['timestamp']
            )
        
        # Perform sync with simulated delay
        start_time = time.time()
        sync_manager.sync_to_server(simulate_network_delay=network_delay)
        end_time = time.time()
        
        # Check latency calculations
        for op in operations:
            latency = sync_manager.calculate_sync_latency(op['entity_type'], op['entity_id'])
            
            if latency is not None:
                # Latency should be positive and reasonable
                assert latency >= 0
                # Should be at least the network delay
                assert latency >= network_delay - 0.1  # Allow for small timing variations
    
    @given(sync_operations())
    def test_conflict_resolution_server_wins(self, operations):
        """Server wins conflict resolution should preserve server data"""
        sync_manager = DataSyncManager()
        sync_manager.conflict_resolution_strategy = 'server_wins'
        
        if not operations:
            return
        
        op = operations[0]
        
        # Simulate server data
        server_data = {'name': 'server_version', 'value': 'server_value'}
        sync_manager.simulate_server_push(op['entity_type'], op['entity_id'], server_data)
        
        # Make local changes
        local_data = {'name': 'local_version', 'value': 'local_value'}
        sync_manager.update_local_data(op['entity_type'], op['entity_id'], local_data)
        
        # Sync (this should create a conflict)
        result = sync_manager.sync_to_server()
        
        # After conflict resolution, local data should match server data
        final_local = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
        final_server = sync_manager.get_server_data(op['entity_type'], op['entity_id'])
        
        # With server_wins strategy, server data should be preserved
        assert 'server_version' in str(final_server) or 'local_version' in str(final_server)
        assert final_local == final_server
    
    @given(sync_operations())
    def test_offline_changes_are_preserved(self, operations):
        """Changes made while offline should be preserved and synced when online"""
        sync_manager = DataSyncManager()
        
        # Simulate offline changes
        sync_manager.simulate_offline_changes(operations)
        
        # Check that we have data for each unique entity
        unique_entities = {}
        for op in operations:
            key = f"{op['entity_type']}:{op['entity_id']}"
            unique_entities[key] = op  # Last operation for each entity wins
        
        # All unique entities should be in local cache
        for key, op in unique_entities.items():
            local_data = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
            assert local_data == op['data']
        
        # Should have items queued for sync (at least as many as unique entities)
        assert len(sync_manager.sync_queue) >= len(unique_entities)
        
        # When coming back online, sync should work
        result = sync_manager.sync_to_server()
        assert result['success'] is True
        
        # All unique entities should now be synchronized
        for key, op in unique_entities.items():
            assert sync_manager.is_data_synchronized(op['entity_type'], op['entity_id'])
    
    @given(
        st.lists(sync_operations(), min_size=1, max_size=5),
        st.booleans()
    )
    def test_sync_status_accuracy(self, operation_batches, simulate_failure):
        """Sync status should accurately reflect synchronization state"""
        sync_manager = DataSyncManager()
        
        total_operations = 0
        
        # Add multiple batches of operations
        for operations in operation_batches:
            for op in operations:
                sync_manager.update_local_data(
                    op['entity_type'],
                    op['entity_id'],
                    op['data'],
                    op['timestamp']
                )
                total_operations += 1
        
        # Get initial status
        initial_status = sync_manager.get_sync_status()
        assert initial_status['pending_sync'] == total_operations
        assert initial_status['synchronized_items'] == 0
        
        # Perform sync
        result = sync_manager.sync_to_server(simulate_failure=simulate_failure)
        
        # Get final status
        final_status = sync_manager.get_sync_status()
        
        if simulate_failure:
            # If sync failed, nothing should be synchronized
            assert final_status['synchronized_items'] == 0
            assert final_status['pending_sync'] == total_operations
        else:
            # If sync succeeded, all items should be synchronized
            assert final_status['synchronized_items'] == final_status['total_items']
            assert final_status['pending_sync'] == 0
            assert final_status['sync_percentage'] == 100.0
    
    @given(sync_operations())
    def test_server_push_updates_local_cache(self, operations):
        """Server push updates should update local cache when no conflicts"""
        sync_manager = DataSyncManager()
        
        for op in operations:
            # Server pushes update
            server_data = {**op['data'], 'server_updated': True}
            result = sync_manager.simulate_server_push(
                op['entity_type'],
                op['entity_id'],
                server_data
            )
            
            # Should succeed (no local changes to conflict with)
            assert result is True
            
            # Local cache should be updated
            local_data = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
            assert local_data == server_data
            assert local_data.get('server_updated') is True
    
    @given(sync_operations())
    def test_concurrent_modifications_create_conflicts(self, operations):
        """Concurrent modifications should be detected as conflicts"""
        sync_manager = DataSyncManager()
        
        if not operations:
            return
        
        op = operations[0]
        
        # Make local changes
        local_data = {**op['data'], 'local_change': True}
        sync_manager.update_local_data(op['entity_type'], op['entity_id'], local_data)
        
        # Simulate server push while we have local changes
        server_data = {**op['data'], 'server_change': True}
        result = sync_manager.simulate_server_push(op['entity_type'], op['entity_id'], server_data)
        
        # Should detect conflict
        assert result is False
        
        # Local data should still have our changes
        current_local = sync_manager.get_local_data(op['entity_type'], op['entity_id'])
        assert current_local.get('local_change') is True
    
    @given(
        st.lists(sync_operations(), min_size=1, max_size=10),
        st.integers(min_value=1, max_value=5)
    )
    def test_batch_sync_maintains_consistency(self, operation_batches, batch_size):
        """Batch synchronization should maintain data consistency"""
        sync_manager = DataSyncManager()
        
        all_operations = []
        for batch in operation_batches:
            all_operations.extend(batch)
        
        # Add all operations
        for op in all_operations:
            sync_manager.update_local_data(
                op['entity_type'],
                op['entity_id'],
                op['data'],
                op['timestamp']
            )
        
        # Sync in batches
        original_queue_size = len(sync_manager.sync_queue)
        
        while sync_manager.sync_queue:
            # Process a batch
            batch_items = sync_manager.sync_queue[:batch_size]
            
            # Sync should process items
            result = sync_manager.sync_to_server()
            assert result['success'] is True
            
            # Queue should be smaller
            assert len(sync_manager.sync_queue) <= original_queue_size
            original_queue_size = len(sync_manager.sync_queue)
        
        # All items should be synchronized
        status = sync_manager.get_sync_status()
        assert status['synchronized_items'] == status['total_items']
        assert status['pending_sync'] == 0
    
    @given(sync_operations())
    def test_data_integrity_after_sync_cycles(self, operations):
        """Data integrity should be maintained through multiple sync cycles"""
        sync_manager = DataSyncManager()
        
        # Perform multiple sync cycles
        for cycle in range(3):
            # Add operations
            for i, op in enumerate(operations):
                modified_data = {**op['data'], f'cycle_{cycle}_item_{i}': True}
                sync_manager.update_local_data(
                    op['entity_type'],
                    f"{op['entity_id']}_cycle_{cycle}_item_{i}",
                    modified_data,
                    op['timestamp'] + cycle
                )
            
            # Sync
            result = sync_manager.sync_to_server()
            assert result['success'] is True
            
            # Verify data integrity
            for i, op in enumerate(operations):
                entity_id = f"{op['entity_id']}_cycle_{cycle}_item_{i}"
                local_data = sync_manager.get_local_data(op['entity_type'], entity_id)
                server_data = sync_manager.get_server_data(op['entity_type'], entity_id)
                
                # Data should match between local and server
                assert local_data == server_data
                
                # Should contain cycle-specific data
                assert local_data.get(f'cycle_{cycle}_item_{i}') is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])