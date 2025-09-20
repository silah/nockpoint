import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
} from 'react-native';
import { Button, Card, ListItem, Avatar } from 'react-native-elements';
import { useAuth } from '../utils/AuthContext';
import ApiService from '../services/ApiService';

const WelcomeScreen = () => {
  const { user, logout } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      // Get upcoming events
      const eventsData = await ApiService.getUpcomingEvents();
      setEvents(eventsData);
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('Error', 'Failed to load data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadData();
  }, []);

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Logout',
          onPress: logout,
        },
      ]
    );
  };

  const formatEventDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getEventTypeColor = (eventType) => {
    switch (eventType) {
      case 'competition':
        return '#e74c3c';
      case 'beginners_course':
        return '#f39c12';
      default:
        return '#3498db';
    }
  };

  const handleEventPress = (event) => {
    // Navigate to event details screen (to be implemented)
    Alert.alert('Event Details', `Selected: ${event.title}`);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* User Welcome Card */}
      <Card containerStyle={styles.welcomeCard}>
        <View style={styles.welcomeHeader}>
          <Avatar
            size="large"
            rounded
            title={user?.username?.charAt(0).toUpperCase() || 'U'}
            backgroundColor="#3498db"
          />
          <View style={styles.welcomeText}>
            <Text style={styles.welcomeTitle}>
              Welcome back, {user?.username || 'Member'}!
            </Text>
            <Text style={styles.welcomeSubtitle}>
              {user?.email || 'member@nockpoint.com'}
            </Text>
            {user?.is_admin && (
              <Text style={styles.adminBadge}>Administrator</Text>
            )}
          </View>
        </View>
        
        <Button
          title="Logout"
          onPress={handleLogout}
          buttonStyle={styles.logoutButton}
          titleStyle={styles.logoutButtonText}
          type="outline"
        />
      </Card>

      {/* Upcoming Events */}
      <Card containerStyle={styles.eventsCard}>
        <Text style={styles.sectionTitle}>Upcoming Events</Text>
        
        {events.length === 0 ? (
          <Text style={styles.noEventsText}>No upcoming events</Text>
        ) : (
          events.map((event, index) => (
            <ListItem
              key={event.id}
              onPress={() => handleEventPress(event)}
              bottomDivider={index < events.length - 1}
              containerStyle={styles.eventItem}
            >
              <View
                style={[
                  styles.eventTypeIndicator,
                  { backgroundColor: getEventTypeColor(event.event_type) },
                ]}
              />
              <ListItem.Content>
                <ListItem.Title style={styles.eventTitle}>
                  {event.title}
                </ListItem.Title>
                <ListItem.Subtitle style={styles.eventDate}>
                  {formatEventDate(event.event_date)}
                </ListItem.Subtitle>
                <ListItem.Subtitle style={styles.eventLocation}>
                  📍 {event.location}
                </ListItem.Subtitle>
                {event.user_registered && (
                  <Text style={styles.registeredBadge}>✓ Registered</Text>
                )}
                {event.max_participants && (
                  <Text style={styles.capacityText}>
                    Spots: {event.available_spots || 0}/{event.max_participants}
                  </Text>
                )}
              </ListItem.Content>
              <ListItem.Chevron />
            </ListItem>
          ))
        )}
      </Card>

      {/* Quick Actions */}
      <Card containerStyle={styles.actionsCard}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <Button
          title="View All Events"
          onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon')}
          buttonStyle={[styles.actionButton, { backgroundColor: '#3498db' }]}
          containerStyle={styles.actionButtonContainer}
        />
        
        <Button
          title="Competitions"
          onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon')}
          buttonStyle={[styles.actionButton, { backgroundColor: '#e74c3c' }]}
          containerStyle={styles.actionButtonContainer}
        />
        
        <Button
          title="My Profile"
          onPress={() => Alert.alert('Coming Soon', 'This feature will be available soon')}
          buttonStyle={[styles.actionButton, { backgroundColor: '#27ae60' }]}
          containerStyle={styles.actionButtonContainer}
        />
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  welcomeCard: {
    margin: 10,
    borderRadius: 10,
    elevation: 3,
  },
  welcomeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  welcomeText: {
    marginLeft: 15,
    flex: 1,
  },
  welcomeTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 5,
  },
  adminBadge: {
    fontSize: 12,
    color: '#e74c3c',
    fontWeight: 'bold',
  },
  logoutButton: {
    borderColor: '#e74c3c',
    borderWidth: 1,
  },
  logoutButtonText: {
    color: '#e74c3c',
  },
  eventsCard: {
    margin: 10,
    borderRadius: 10,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  noEventsText: {
    textAlign: 'center',
    color: '#7f8c8d',
    fontSize: 16,
    padding: 20,
  },
  eventItem: {
    paddingVertical: 15,
  },
  eventTypeIndicator: {
    width: 4,
    height: '100%',
    borderRadius: 2,
    marginRight: 10,
  },
  eventTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  eventDate: {
    fontSize: 14,
    color: '#3498db',
    marginBottom: 3,
  },
  eventLocation: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 5,
  },
  registeredBadge: {
    fontSize: 12,
    color: '#27ae60',
    fontWeight: 'bold',
  },
  capacityText: {
    fontSize: 12,
    color: '#f39c12',
  },
  actionsCard: {
    margin: 10,
    borderRadius: 10,
    elevation: 3,
    marginBottom: 20,
  },
  actionButton: {
    borderRadius: 8,
    paddingVertical: 12,
  },
  actionButtonContainer: {
    marginBottom: 10,
  },
});

export default WelcomeScreen;