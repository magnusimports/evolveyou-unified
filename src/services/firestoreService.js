import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  setDoc, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy, 
  limit,
  serverTimestamp,
  writeBatch
} from 'firebase/firestore';
import { db } from '../config/firebase';

class FirestoreService {
  // Operações de usuários
  async getUserProfile(userId) {
    try {
      const userDoc = await getDoc(doc(db, 'users', userId));
      return userDoc.exists() ? { id: userDoc.id, ...userDoc.data() } : null;
    } catch (error) {
      console.error('Erro ao buscar perfil do usuário:', error);
      throw error;
    }
  }

  async updateUserProfile(userId, data) {
    try {
      const userRef = doc(db, 'users', userId);
      await updateDoc(userRef, {
        ...data,
        updatedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Erro ao atualizar perfil do usuário:', error);
      throw error;
    }
  }

  async saveAnamneseResults(userId, anamneseData, calculations) {
    try {
      const userRef = doc(db, 'users', userId);
      await updateDoc(userRef, {
        anamnese: anamneseData,
        calculations: calculations,
        anamneseCompletedAt: serverTimestamp(),
        onboardingCompleted: true,
        anamneseCompleted: true,
        updatedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Erro ao salvar resultados da anamnese:', error);
      throw error;
    }
  }

  // Operações de alimentos
  async getFoodDatabase() {
    try {
      const foodsCollection = collection(db, 'evolveyou-foods');
      const foodsSnapshot = await getDocs(foodsCollection);
      return foodsSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
      console.error('Erro ao buscar base de alimentos:', error);
      throw error;
    }
  }

  async searchFoods(searchTerm, category = null) {
    try {
      let q = collection(db, 'evolveyou-foods');
      
      if (category) {
        q = query(q, where('categoria', '==', category));
      }
      
      const snapshot = await getDocs(q);
      const foods = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      
      // Filtrar por termo de busca (client-side para simplicidade)
      if (searchTerm) {
        return foods.filter(food => 
          food.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
          food.categoria.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }
      
      return foods;
    } catch (error) {
      console.error('Erro ao buscar alimentos:', error);
      throw error;
    }
  }

  // Operações de refeições
  async saveMeal(userId, mealData) {
    try {
      const mealsCollection = collection(db, 'users', userId, 'meals');
      const mealRef = doc(mealsCollection);
      await setDoc(mealRef, {
        ...mealData,
        createdAt: serverTimestamp()
      });
      return mealRef.id;
    } catch (error) {
      console.error('Erro ao salvar refeição:', error);
      throw error;
    }
  }

  async getMeals(userId, date = null) {
    try {
      let q = collection(db, 'users', userId, 'meals');
      
      if (date) {
        const startOfDay = new Date(date);
        startOfDay.setHours(0, 0, 0, 0);
        const endOfDay = new Date(date);
        endOfDay.setHours(23, 59, 59, 999);
        
        q = query(q, 
          where('date', '>=', startOfDay),
          where('date', '<=', endOfDay),
          orderBy('date', 'desc')
        );
      } else {
        q = query(q, orderBy('createdAt', 'desc'), limit(50));
      }
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
      console.error('Erro ao buscar refeições:', error);
      throw error;
    }
  }

  // Operações de exercícios
  async getExerciseDatabase() {
    try {
      const exercisesCollection = collection(db, 'exercicios');
      const exercisesSnapshot = await getDocs(exercisesCollection);
      return exercisesSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
      console.error('Erro ao buscar base de exercícios:', error);
      throw error;
    }
  }

  async searchExercises(searchTerm, category = null) {
    try {
      let q = collection(db, 'exercicios');
      
      if (category) {
        q = query(q, where('categoria', '==', category));
      }
      
      const snapshot = await getDocs(q);
      const exercises = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      
      // Filtrar por termo de busca
      if (searchTerm) {
        return exercises.filter(exercise => 
          exercise.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
          exercise.categoria.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }
      
      return exercises;
    } catch (error) {
      console.error('Erro ao buscar exercícios:', error);
      throw error;
    }
  }

  // Operações de treinos
  async saveWorkout(userId, workoutData) {
    try {
      const workoutsCollection = collection(db, 'users', userId, 'workouts');
      const workoutRef = doc(workoutsCollection);
      await setDoc(workoutRef, {
        ...workoutData,
        createdAt: serverTimestamp()
      });
      return workoutRef.id;
    } catch (error) {
      console.error('Erro ao salvar treino:', error);
      throw error;
    }
  }

  async getWorkouts(userId) {
    try {
      const q = query(
        collection(db, 'users', userId, 'workouts'),
        orderBy('createdAt', 'desc'),
        limit(50)
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
      console.error('Erro ao buscar treinos:', error);
      throw error;
    }
  }

  async saveWorkoutExecution(userId, workoutId, executionData) {
    try {
      const executionsCollection = collection(db, 'users', userId, 'workout-executions');
      const executionRef = doc(executionsCollection);
      await setDoc(executionRef, {
        workoutId,
        ...executionData,
        executedAt: serverTimestamp()
      });
      return executionRef.id;
    } catch (error) {
      console.error('Erro ao salvar execução de treino:', error);
      throw error;
    }
  }

  // Operações de progresso
  async saveProgressEntry(userId, progressData) {
    try {
      const progressCollection = collection(db, 'users', userId, 'progress');
      const progressRef = doc(progressCollection);
      await setDoc(progressRef, {
        ...progressData,
        recordedAt: serverTimestamp()
      });
      return progressRef.id;
    } catch (error) {
      console.error('Erro ao salvar progresso:', error);
      throw error;
    }
  }

  async getProgressHistory(userId, days = 30) {
    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);
      
      const q = query(
        collection(db, 'users', userId, 'progress'),
        where('recordedAt', '>=', cutoffDate),
        orderBy('recordedAt', 'desc')
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
      console.error('Erro ao buscar histórico de progresso:', error);
      throw error;
    }
  }

  // Operações em lote
  async batchWrite(operations) {
    try {
      const batch = writeBatch(db);
      
      operations.forEach(operation => {
        const { type, ref, data } = operation;
        
        switch (type) {
          case 'set':
            batch.set(ref, data);
            break;
          case 'update':
            batch.update(ref, data);
            break;
          case 'delete':
            batch.delete(ref);
            break;
          default:
            throw new Error(`Tipo de operação inválido: ${type}`);
        }
      });
      
      await batch.commit();
    } catch (error) {
      console.error('Erro ao executar operações em lote:', error);
      throw error;
    }
  }
}

export default new FirestoreService();

