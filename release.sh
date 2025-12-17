#!/bin/bash

# Check if git is installed
if ! command -v git &> /dev/null
then
    echo "git could not be found, please install git."
    exit 1
fi

# Ask for version number
read -p "Enter the version number (e.g., 1.0.0): " version_number

# Validate input (basic validation, ensures it's not empty)
if [ -z "$version_number" ]; then
    echo "Version number cannot be empty. Aborting."
    exit 1
fi

# Ask for release name
read -p "Enter the release name: " release_name

# Validate input (basic validation, ensures it's not empty)
if [ -z "$release_name" ]; then
    echo "Release name cannot be empty. Aborting."
    exit 1
fi

# Create the annotated tag
tag_name="v${version_number}"
echo "Creating git tag: ${tag_name} with message: ${release_name}"
git tag -a "$tag_name" -m "$release_name"

# Push the tag
echo "Pushing tag to remote..."
git push origin "$tag_name"

if [ $? -eq 0 ]; then
    echo "Successfully pushed tag ${tag_name}. The release workflow should now be triggered."
else
    echo "Failed to push tag. Please check your git configuration and try again."
fi
