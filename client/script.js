// script.js
const { createApp, ref, onMounted } = Vue;

createApp({
  setup() {
    const posts = ref([]);
    const loading = ref(true);
    const showModal = ref(false); // Controls the popup
    const newPostContent = ref(""); // Binds to textarea
    const currentAccountId = ref(1); // Use '1' to match your Alice seed data

    // 1. Fetch data from your Flask API
    const fetchFeed = async () => {
      loading.value = true; // Ensure it starts as true
      const id = currentAccountId.value;
      try {
        const response = await fetch(`http://localhost:5000/api/feed/${id}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
    
        const data = await response.json();
        posts.value = data;
      } catch (error) {
        console.error("CRITICAL ERROR:", error);
        // Show a fake post so the user knows the connection failed
        posts.value = [{ 
            username: 'System', 
            content: '⚠️ Connection Error: Is your Flask server running on port 5000?', 
            post_id: -1 
        }];
      } finally {
        // This MUST run to hide the loading screen
        loading.value = false; 
      }
    };

    // 2. Helper to make SQLite timestamps look pretty
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    };

    const submitPost = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_id: currentAccountId,
            content: newPostContent.value
          })
        });

        const result = await response.json();
        if (result.success) {
          // Reset UI
          newPostContent.value = "";
          showModal.value = false;
          // Refresh feed to show the new post
          fetchFeed();
        }
      } catch (error) {
        alert("Error saving post: " + error.message);
      }
    };

    // Run when the page loads
    onMounted(fetchFeed);

    return {
      posts,
      loading,
      showModal,
      newPostContent,
      submitPost,
      formatDate: (d) => new Date(d).toLocaleString()
    };
  }
}).mount('#app');
