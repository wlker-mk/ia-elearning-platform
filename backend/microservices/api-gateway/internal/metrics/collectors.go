package metrics

type Collector interface {
	Collect() map[string]interface{}
}
