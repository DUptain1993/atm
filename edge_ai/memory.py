from datetime import datetime

class Memory:
    """Conversation memory manager"""
    
    def __init__(self, db):
        self.db = db
        self.context_window = 10
        self.working_memory = []
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def add(self, user_input, ai_response):
        """Add to memory"""
        # Add to working memory
        self.working_memory.append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Trim if too large
        if len(self.working_memory) > self.context_window * 2:
            self.working_memory = self.working_memory[-self.context_window * 2:]
        
        # Save to persistent storage
        self.db.add_memory(user_input, ai_response)
    
    def context(self):
        """Get conversation context"""
        if not self.working_memory:
            return ""
        
        # Get last N turns
        recent = self.working_memory[-self.context_window:]
        context_parts = []
        for turn in recent:
            context_parts.append(f"User: {turn['user']}")
            context_parts.append(f"AI: {turn['ai']}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear working memory"""
        self.working_memory = []
    
    def get_summary(self):
        """Get memory summary"""
        return {
            'total_turns': len(self.working_memory),
            'session_id': self.session_id,
            'context_window': self.context_window,
            'last_turn': self.working_memory[-1] if self.working_memory else None
        }
