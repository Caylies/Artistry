# Generation

Generation requires the **Can Generate** permission. The generation process will start once the generate command (`/artistry generate`) is executed.

## Process

1. All threads from the configured forum channel will be fetched.
2. Threads that dont match any countryball's name and isn't marked as a safe thread will be deleted.
3. Missing threads will be created with their starter message pinned.

## Duration

Duration depends on how many countryballs are registered. If 400 countryballs are registered, generation can take up to **40 minutes** to complete. The duration is caused by Discord rate limits and cannot be controlled by Artistry.
