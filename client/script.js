// script.js
const { createApp, ref, onMounted, toRaw } = Vue; // Added toRaw here

createApp({
  setup() {
    const posts = ref([]);
    const loading = ref(true);
    const showModal = ref(false); 
    const newPostContent = ref(""); 
    const currentAccountId = ref(1); 
    const isSubmitting = ref(false);

    // 1. Fetch data from your Flask API
    const fetchFeed = async () => {
      loading.value = true;
      const id = currentAccountId.value;
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/feed/${id}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
    
        const data = await response.json();
        posts.value = data;
      } catch (error) {
        console.error("CRITICAL ERROR:", error);
        posts.value = [{ 
            username: 'System', 
            content: '⚠️ Connection Error: Is your Flask server running?', 
            post_id: -1 
        }];
      } finally {
        loading.value = false; 
      }
    };

    // 2. Formatting helper
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

    // 3. Submit a new post
    const submitPost = async () => {
      isSubmitting.value = true;
      
      // Use a temporary constant to hold the number
      const idToSend = Number(currentAccountId.value);
      const contentToSend = String(newPostContent.value);
    
      console.log("Sending clean ID:", idToSend);
    
      try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_id: idToSend, // No objects, just the number
            content: contentToSend
          })
        });
        
        const result = await response.json();
        if (result.success) {
          newPostContent.value = "";
          showModal.value = false;
          await fetchFeed(); 
        } else {
          console.error("Flask Error:", result.error);
        }
      } catch (error) {
        console.error("Fetch Error:", error);
      } finally {
        isSubmitting.value = false;
      }
    };

    // Initialize
    onMounted(fetchFeed);

    return {
      posts,
      loading,
      showModal,
      newPostContent,
      isSubmitting,
      submitPost,
      formatDate
    };
  } // This was the missing setup brace!
}).mount('#app');