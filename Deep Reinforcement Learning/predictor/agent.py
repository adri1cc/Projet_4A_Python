import random
import numpy as np
import pandas as pd
from collections import deque
import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
tf.config.optimizer.set_jit(True)
from tensorflow import keras
from keras.layers import Dense, LSTM
from keras.models import Sequential, clone_model
import keras.backend as K
import os


class DQLAgent:
    def __init__(self, hidden_units, learning_rate, batch,
                 train_env, test_env):
        self.train_env = train_env
        self.test_env = test_env
        self.epsilon = 1.0 # Représente la probabilité de décision aléatoire
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.98 # Décalage entre chaque epoch
        self.learning_rate = learning_rate
        self.gamma = 0.98 #Importance du gain suivant -> 0 vision court terme -> 1 prends en compte les valeurs futures avec plus dimportance que les passée (0.5)
        self.tau = 0.001 #Vitesse de mise à jour des poids du réseau
        self.batch = batch
        self.batch_size = 256 #plus c'est haut plus on va avoir tendance à stabiliser le système valeurs courantes (16-512)
        self.mini_batch_size = 16
        self.max_treward = 0
        self.trewards = list()
        self.losses = list()
        self.sharpes = list()
        self.averages = list()
        self.performances = list()
        self.aperformances = list()
        self.vperformances = list()
        self.data = pd.DataFrame()
        self.memory = deque(maxlen=10000) 
       
        self.value_model = self._build_lstm_model(hidden_units, learning_rate)
        self.target_model = clone_model(self.value_model)
        self.target_model.set_weights(self.value_model.get_weights())


    def _build_lstm_model(self, hu, lr):
        model = Sequential()
        model.add(LSTM(int(hu), return_sequences=True, input_shape=(self.train_env.lags, 
            self.train_env.n_features)))
        model.add(LSTM(int(hu/2), return_sequences=False))
        model.add(Dense(int(hu/2),activation='relu'))
        model.add(Dense(2, activation='linear'))
        model.compile(
            loss=self._huber_loss,
            optimizer=keras.optimizers.Adam(learning_rate=lr)
        )
        return model

    def _hard_update(self):
        self.target_model.set_weights(self.value_model.get_weights)

    def _soft_update(self):
        target_weights = self.target_model.get_weights()
        value_weights = self.value_model.get_weights()
        new_weights = [self.tau * tw + (1 - self.tau) * vw for tw, vw in zip(target_weights, value_weights)]
        self.target_model.set_weights(new_weights)

    def _huber_loss(self, y_true, y_pred, clip_delta=1.0):
        """Huber loss - Custom Loss Function for Q Learning"""
        error = y_true - y_pred
        cond = K.abs(error) <= clip_delta
        squared_loss = 0.5 * K.square(error)
        quadratic_loss = 0.5 * K.square(clip_delta) + clip_delta * (K.abs(error) - clip_delta)
        return K.mean(tf.where(cond, squared_loss, quadratic_loss))

    def act(self, state):
        if random.random() <= self.epsilon:
            return self.train_env.action_space.sample()
        action = self.value_model.predict(state, verbose=0)[0]
        return np.argmax(action)
    
    def replay_batch(self, episode):
        # Update the target network with a soft update
        self._soft_update()

        # Sample a batch of experiences from the agent's memory
        batch = random.sample(self.memory, self.batch_size)
        losses = []

        # Iterate over mini-batches within the sampled batch
        for i in range(0, self.batch_size, self.mini_batch_size):
            mini_batch = batch[i:i + self.mini_batch_size]

            # Extract and convert the mini-batch components into numpy arrays
            states, actions, rewards, next_states, dones = map(np.array, zip(*mini_batch))

            # Use the target network to predict Q-values for the next states
            future_qs = self.target_model.predict(next_states, verbose=0)

            # Use the value model to predict Q-values for the current states
            current_qs = self.value_model.predict(states, verbose=0)

            # Update Q-values in the mini-batch based on rewards and next state Q-values
            updated_qs = np.copy(current_qs)
            for i in range(self.mini_batch_size):
                if dones[i]:
                    updated_qs[i, actions[i]] = rewards[i]
                else:
                    updated_qs[i, actions[i]] = rewards[i] + self.gamma * np.amax(future_qs[i])

            # Train the value model on the mini-batch and get the loss
            loss = self.value_model.fit(states, updated_qs, epochs=1, verbose=False).history['loss'][0]
            losses.append(loss)

        # Decay the exploration rate (epsilon) over time
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Return the mean loss over all mini-batches in the sampled batch
        return np.mean(np.array(losses))

    
    def replay_serial(self, epsiode):
        losses = []
        # soft update for target network 
        self._soft_update() 

        batch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in batch:
            next_state = np.reshape(next_state, [1, self.train_env.lags,
                                       self.train_env.n_features])

            target = self.value_model.predict(state, verbose=0)
            future_q = self.target_model.predict(next_state, verbose=0)[0]
            #target = np.copy(current_q)
            if not done:
                reward += self.gamma ^ epsiode * np.amax(future_q) # A voir si c'est bon la puissance
            target[0, action] = reward
           
            loss = self.value_model.fit(state, target, epochs=1, verbose=False).history["loss"][0]
            losses.append(loss)
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return np.mean(np.array(losses))

    def learn(self, episodes):
        # Loop through episodes
        for e in range(1, episodes + 1):
            # Print features of the training environment
            print(self.train_env.features)

            # Reset the environment and reshape the initial state
            batch_state = self.train_env.reset()
            state = np.reshape(batch_state, [1, self.train_env.lags, self.train_env.n_features])
            treward = 0

            # Loop through steps in the episode
            for _ in range(10000):
                # Choose an action using the epsilon-greedy policy
                action = self.act(state)

                # Take a step in the environment based on the chosen action
                next_batch_state, reward, done, info = self.train_env.step(action)

                # Reshape the next state and store the experience in memory
                next_state = np.reshape(next_batch_state, [1, self.train_env.lags, self.train_env.n_features])
                self.memory.append([batch_state, action, reward, next_batch_state, done])
                state = next_state
                treward += reward

                # Check if the episode is done
                if done:
                    # Update various performance metrics and print the episode summary
                    self.trewards.append(treward)
                    av = sum(self.trewards[-5:]) / 5
                    perf = self.train_env.performance
                    sharpe = self.train_env.sharpe
                    self.sharpes.append(sharpe)
                    self.averages.append(av)
                    self.performances.append(perf)
                    self.aperformances.append(sum(self.performances[-5:]) / 5)
                    self.max_treward = max(self.max_treward, treward)

                    # If enough experiences are in memory, perform replay training
                    if len(self.memory) > self.batch_size:
                        if self.batch:
                            loss = self.replay_batch(e)
                        else:
                            loss = self.replay_serial(e)

                        self.losses.append(loss)
                    else:
                        loss = 0.0

                    # Print episode summary and break the inner loop
                    templ = 'episode: {:>3d}/{:<3d} | loss: {:>.5f} | perf: {:>8.3%} | endurance: {:>4d} | total reward: {:>6.2f} | epsilon: {:>3.2}'
                    print(templ.format(e, episodes, loss, (perf-1), (_ + 1), treward, self.epsilon))
                    break

            # Save the model every 25 episodes
            if e % 25 == 0:
                model_dir = 'models\{}_e{}_lags{}_tau{}_gamma_{}'.format(
                            self.train_env.symbol[0].split('_')[0], 
                            e, self.train_env.lags,  
                            str(self.tau).replace('.', '_'),
                            str(self.gamma).replace('.', '_')
                            )
                
                # Create directory if it doesn't exist
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)

                model_name = 'model.h5' 
                full_model_path = os.path.join(model_dir, model_name)

                print(f"Saving model to {full_model_path}")
                
                # Save model weights
                self.value_model.save_weights(full_model_path)

            # Validate the model every 555 episodes
            if e % 555 == 0:
                self.validate(e, episodes)

        # Print an empty line at the end of all episodes
        print()

    def validate(self, e, episodes):
        batch_state = self.test_env.reset()
        # add dimnesion to state 
        state = np.reshape(batch_state, [1, self.test_env.lags,
                                   self.test_env.n_features])
        treward = 0
        for _ in range(10000):
            action = np.argmax(self.value_model.predict(state, verbose=0)[0])
            next_batch_state, reward, done, info = self.test_env.step_val(action)
            # add dimnesion to state  
            state = np.reshape(next_batch_state, [1, self.test_env.lags,
                                   self.test_env.n_features])
            treward += reward 
            if done:
                perf = self.test_env.performance
                self.vperformances.append(perf)
                precision = (treward)  / (len(self.test_env.data) - self.test_env.lags)               
                if e % 50 == 0:
                    templ = 80 * '='
                    templ += '\nepisode: {:>3d}/{:<3d} | VALIDATION | precision: {:>.2%} |'
                    templ += 'perf: {:>7.3%} | eps: {:>.2f}\n'
                    templ += 80 * '='
                    print(templ.format(e, episodes, precision,
                                       (perf-1), self.epsilon))
                                    
                break