import asyncio
import sys
import os

# Add the parent directory to Python path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.main import generate_video

# List of JavaScript interview topics
JS_TOPICS = [
    "Create a video explaining JavaScript Event Loop in a simple way. Show how call stack, callback queue, and microtask queue work together. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Arrow Functions vs Regular Functions. Cover key differences like 'this' binding and syntax benefits. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Promises and Async/Await. Show how they make asynchronous code easier to write and read. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Closures with practical examples. Show how they help in data privacy and maintaining state. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Prototypal Inheritance vs Classical Inheritance. Show how objects inherit from other objects. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Hoisting with examples. Cover variable and function hoisting behavior. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Map and Set data structures. Show their benefits over regular objects and arrays. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Event Bubbling and Capturing. Show how events propagate through the DOM tree. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Modules (ES6 Modules). Cover import/export syntax and benefits of modular code. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'",
    
    "Create a video explaining JavaScript Memory Management and Garbage Collection. Show how JS manages memory automatically. End by saying: 'Comment below to get the free video generator link — I'll DM it to you!'"
]

async def generate_js_interview_videos():
    """Generate a series of JavaScript interview topic videos"""
    for i, topic in enumerate(JS_TOPICS, 1):
        print(f"\n🎥 Generating video {i}/10: {topic[:50]}...")
        try:
            video_path = await generate_video(
                video_type="family_guy",
                topic=topic
            )
            print(f"✅ Video {i} generated successfully: {video_path}")
        except Exception as e:
            print(f"❌ Error generating video {i}: {str(e)}")
            continue

if __name__ == "__main__":
    asyncio.run(generate_js_interview_videos())