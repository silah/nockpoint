#!/usr/bin/env python
"""
Data migration script to convert Nockpoint from single-tenant to multi-tenant.

This script:
1. Creates a default club from existing ClubSettings
2. Migrates all users to ClubMembership with the default club
3. Assigns club_id to all existing data (inventory, events, competitions, etc.)

Run this AFTER generating and applying the database migration that adds the new columns.

Usage:
    python migrate_to_multitenancy.py
"""

from app import create_app, db
from app.models import (
    Club, ClubMembership, User, ClubSettings,
    InventoryCategory, InventoryItem, ShootingEvent,
    Competition, BeginnersStudent
)
from datetime import datetime
import sys

def migrate_to_multi_tenancy():
    """Migrate existing single-tenant data to multi-tenant structure"""
    
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("NOCKPOINT MULTI-TENANCY MIGRATION")
        print("=" * 70)
        print()
        
        # Check if default club already exists
        existing_club = Club.query.filter_by(slug='default').first()
        if existing_club:
            print("⚠️  Default club already exists!")
            print(f"   Club: {existing_club.name}")
            response = input("Do you want to continue with existing club? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return
            default_club = existing_club
        else:
            # Step 1: Create default club from existing settings
            print("Step 1: Creating default club from ClubSettings...")
            settings = ClubSettings.query.first()
            
            default_club = Club(
                name=settings.club_name if settings else "Nockpoint Archery Club",
                slug="default",
                description=settings.description if settings else None,
                email=settings.email if settings else None,
                phone=settings.phone if settings else None,
                address=settings.address if settings else None,
                website_url=settings.website_url if settings else None,
                facebook_url=settings.facebook_url if settings else None,
                instagram_url=settings.instagram_url if settings else None,
                twitter_url=settings.twitter_url if settings else None,
                default_location=settings.default_location if settings else None,
                activation_code=settings.activation_code if settings else None,
                annual_membership_price=settings.annual_membership_price if settings else 0.00,
                quarterly_membership_price=settings.quarterly_membership_price if settings else 0.00,
                monthly_membership_price=settings.monthly_membership_price if settings else 0.00,
                per_event_price=settings.per_event_price if settings else 0.00,
                is_pro_enabled=settings.is_pro_enabled if settings else False,
                pro_subscription_id=settings.pro_subscription_id if settings else None,
                pro_expires_at=settings.pro_expires_at if settings else None,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(default_club)
            db.session.flush()  # Get the ID without committing
            
            print(f"✅ Created default club: {default_club.name} (ID: {default_club.id})")
        
        # Step 2: Migrate users to ClubMembership
        print("\nStep 2: Migrating users to ClubMembership...")
        users = User.query.all()
        migrated_users = 0
        
        for user in users:
            # Check if membership already exists
            existing_membership = ClubMembership.query.filter_by(
                user_id=user.id,
                club_id=default_club.id
            ).first()
            
            if not existing_membership:
                membership = ClubMembership(
                    user_id=user.id,
                    club_id=default_club.id,
                    role=user.role if user.role else 'member',
                    membership_type=user.membership_type if user.membership_type else 'monthly',
                    is_active=user.is_active,
                    joined_at=user.created_at
                )
                db.session.add(membership)
                migrated_users += 1
        
        print(f"✅ Created {migrated_users} club memberships")
        
        # Step 3: Add club_id to inventory categories
        print("\nStep 3: Migrating inventory categories...")
        categories = InventoryCategory.query.filter(
            (InventoryCategory.club_id == None) | (InventoryCategory.club_id == 0)
        ).all()
        
        for category in categories:
            category.club_id = default_club.id
        
        print(f"✅ Migrated {len(categories)} inventory categories")
        
        # Step 4: Add club_id to inventory items
        print("\nStep 4: Migrating inventory items...")
        items = InventoryItem.query.filter(
            (InventoryItem.club_id == None) | (InventoryItem.club_id == 0)
        ).all()
        
        for item in items:
            item.club_id = default_club.id
        
        print(f"✅ Migrated {len(items)} inventory items")
        
        # Step 5: Add club_id to shooting events
        print("\nStep 5: Migrating shooting events...")
        events = ShootingEvent.query.filter(
            (ShootingEvent.club_id == None) | (ShootingEvent.club_id == 0)
        ).all()
        
        for event in events:
            event.club_id = default_club.id
        
        print(f"✅ Migrated {len(events)} shooting events")
        
        # Step 6: Add club_id to competitions
        print("\nStep 6: Migrating competitions...")
        competitions = Competition.query.filter(
            (Competition.club_id == None) | (Competition.club_id == 0)
        ).all()
        
        for competition in competitions:
            competition.club_id = default_club.id
        
        print(f"✅ Migrated {len(competitions)} competitions")
        
        # Step 7: Add club_id to beginners students
        print("\nStep 7: Migrating beginners students...")
        students = BeginnersStudent.query.filter(
            (BeginnersStudent.club_id == None) | (BeginnersStudent.club_id == 0)
        ).all()
        
        for student in students:
            student.club_id = default_club.id
        
        print(f"✅ Migrated {len(students)} beginners students")
        
        # Commit all changes
        print("\nCommitting changes to database...")
        try:
            db.session.commit()
            print("✅ All changes committed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")
            return
        
        # Summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Default Club: {default_club.name}")
        print(f"Club ID: {default_club.id}")
        print(f"Club Slug: {default_club.slug}")
        print(f"\nMigrated:")
        print(f"  - {migrated_users} user memberships")
        print(f"  - {len(categories)} inventory categories")
        print(f"  - {len(items)} inventory items")
        print(f"  - {len(events)} shooting events")
        print(f"  - {len(competitions)} competitions")
        print(f"  - {len(students)} beginners students")
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application to ensure everything works")
        print("2. Update application code to use club context")
        print("3. Implement club registration and switching features")
        print("=" * 70)

if __name__ == '__main__':
    print("\n⚠️  WARNING: This script will modify your database.")
    print("   Make sure you have a backup before proceeding!\n")
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_to_multi_tenancy()
    else:
        print("Migration cancelled.")
        sys.exit(0)
