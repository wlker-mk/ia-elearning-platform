package ratelimit

import "time"

type SlidingWindow struct {
	maxRequests int
	window      time.Duration
}

func NewSlidingWindow(maxRequests int, window time.Duration) *SlidingWindow {
	return &SlidingWindow{
		maxRequests: maxRequests,
		window:      window,
	}
}
