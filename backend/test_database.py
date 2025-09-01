import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import engine, init_models, get_async_session
from app.models.schemas import Character, Story, Memory, Action

async def create_test_data():
    """Create test data to verify database relationships"""
    # Initialize models
    await init_models()

    # Create an async session
    async for session in get_async_session():
        try:
            # Create a test character
            character = Character(
                id=str(uuid.uuid4()),
                name="Test Character",
                description="A test character for database verification",
                personality={
                    "traits": ["brave", "curious"],
                    "goals": ["explore the world"]
                }
            )
            session.add(character)

            # Create a test story
            story = Story(
                id=str(uuid.uuid4()),
                title="Test Adventure",
                description="A test story for database verification",
                current_state={
                    "location": "Unknown",
                    "time": "Afternoon"
                }
            )
            # Add character to story
            story.characters.append(character)
            session.add(story)

            # Create a test memory
            memory = Memory(
                id=str(uuid.uuid4()),
                character_id=character.id,
                content="A vivid memory of past adventures",
                importance=0.8,
                context={
                    "emotion": "excitement",
                    "related_entities": ["mountain", "river"]
                }
            )
            session.add(memory)

            # Create a test action
            action = Action(
                id=str(uuid.uuid4()),
                story_id=story.id,
                character_id=character.id,
                content="Embarking on a new journey",
                action_type="movement",
                reaction="Feeling excited and ready",
                context={
                    "start_location": "village",
                    "destination": "mountains"
                }
            )
            session.add(action)

            # Commit the transaction
            await session.commit()

            print("Test data created successfully!")

            # Verify relationships
            print("\nVerifying Relationships:")
            
            # Check character's memories
            result = await session.execute(select(Character).where(Character.name == "Test Character"))
            test_character = result.scalar_one()
            print(f"Character memories: {len(test_character.memories)}")
            assert len(test_character.memories) == 1, "Character should have 1 memory"
            
            # Check character's stories
            print(f"Character stories: {len(test_character.stories)}")
            assert len(test_character.stories) == 1, "Character should be in 1 story"
            
            # Check story's characters
            result = await session.execute(select(Story).where(Story.title == "Test Adventure"))
            test_story = result.scalar_one()
            print(f"Story characters: {len(test_story.characters)}")
            assert len(test_story.characters) == 1, "Story should have 1 character"
            
            # Check story's actions
            print(f"Story actions: {len(test_story.actions)}")
            assert len(test_story.actions) == 1, "Story should have 1 action"

            print("\nAll relationship tests passed successfully!")

        except Exception as e:
            print(f"Error creating test data: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def main():
    try:
        await create_test_data()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())