package cache

import (
	"sync"
	"time"
)

type MemoryCache struct {
	data map[string]cacheItem
	mu   sync.RWMutex
}

type cacheItem struct {
	value      interface{}
	expiration time.Time
}

func NewMemoryCache() *MemoryCache {
	return &MemoryCache{
		data: make(map[string]cacheItem),
	}
}

func (m *MemoryCache) Get(key string) (interface{}, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	item, exists := m.data[key]
	if !exists || time.Now().After(item.expiration) {
		return nil, nil
	}

	return item.value, nil
}

func (m *MemoryCache) Set(key string, value interface{}, expiration time.Duration) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.data[key] = cacheItem{
		value:      value,
		expiration: time.Now().Add(expiration),
	}

	return nil
}

func (m *MemoryCache) Delete(key string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	delete(m.data, key)
	return nil
}
