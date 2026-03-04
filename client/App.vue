<template>
  <div class="min-h-screen">
    <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 p-4">
      <div class="max-w-5xl mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold text-indigo-600 tracking-tight">SocialSphere</h1>
        <div class="flex gap-4">
          <button class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition">
            New Post
          </button>
        </div>
      </div>
    </nav>

    <main class="max-w-2xl mx-auto py-8 px-4">
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="h-32 bg-gray-100 rounded-xl animate-pulse"></div>
      </div>

      <div v-else-if="posts.length === 0" class="text-center py-20">
        <p class="text-gray-400 italic">No posts yet. Follow someone to see their updates!</p>
      </div>

      <div v-else class="space-y-1">
        <div v-for="post in posts" :key="post.post_id" 
             class="bg-white border border-gray-100 p-6 rounded-xl hover:shadow-sm transition-shadow">
          <div class="flex items-center justify-between mb-3">
            <span class="font-bold text-gray-900">@{{ post.username }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(post.created_at) }}</span>
          </div>
          <p class="text-gray-700 mb-4 whitespace-pre-wrap">{{ post.content }}</p>
          <div class="flex gap-6 text-sm font-medium text-gray-500">
            <span>♥ {{ post.like_count }}</span>
            <span>💬 {{ post.comment_count }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
